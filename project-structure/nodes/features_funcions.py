import pyspark.sql.functions as F
import pyspark.sql.types as T
from pyspark.sql.window import Window
from statistics import variance, mean

def create_monthly_feature_name(col_name, number_of_months):
    feature_name = f"{col_name}_over_last_{number_of_months}_month"
    if (number_of_months) == 1:
        return feature_name
    else:
        return f"{feature_name}s"

def create_daily_feature_name(col_name, number_of_days):
    return f"{col_name}_over_last_{number_of_days}_days"

def create_count_distinct_feature_days_before_prediction_date(df_to_add_feature_to, df_with_feature, date_coll_name, days_before_prediction_date, count_distinct_feature_name, col_name):
    return (
        df_to_add_feature_to.alias("df_add")
        .join(df_with_feature.alias("df_f"), "organization_id", "left")
        .filter(
            ((F.col(f"df_f.{date_coll_name}") >= F.date_sub(F.col("df_add.date_partition"), days_before_prediction_date)) & 
            (F.col(f"df_f.{date_coll_name}") < F.col("df_add.date_partition")))
        )
        # specify id
        .groupBy("df_add.id", "df_add.date_partition")
        .agg(F.countDistinct(count_distinct_feature_name).alias(col_name))
    )

# Usage example: feature_date_col_name = 'date', feature_col_name=full_col_name
def add_previouse_value_for_feature(df_to_add_value, original_feature_df, feature_date_col_name, months_to_subtract, original_feature_col_name, final_col_name):
    window_spec_quantity = Window.partitionBy("id", "date_partition").orderBy(F.col("date").desc())
    previouse_col_name = f"previous_{final_col_name}"
    original_feature_with_date_df = (
        original_feature_df
        .withColumnRenamed(feature_date_col_name, "date")
        .withColumnRenamed("id", "f_id")
    )
    result = (
        df_to_add_value.alias("d")
        .join(original_feature_with_date_df.alias("f"),
              (F.col("d.id") == F.col("f.f_id")) & 
              (F.col(f"f.date") < F.add_months(F.col("d.date_partition"), -months_to_subtract)), "left")
        .withColumn("row_number", F.row_number().over(window_spec_quantity))
        .filter(F.col("row_number") == 1).drop("row_number")
        .select("d.*", F.col(f"f.{original_feature_col_name}").alias(previouse_col_name))
        .withColumn(final_col_name, F.when(F.col(final_col_name).isNull(), F.col(previouse_col_name)).otherwise(F.col(final_col_name)))
        .drop(previouse_col_name)
    )
    return result

def add_monthly_feature(org_date_partition, feature_df, months_to_subtract, feature_col_name):
    full_col_name = create_monthly_feature_name(feature_col_name, months_to_subtract)

    result = (
        org_date_partition.alias("o")
        .join(feature_df.alias("f"),
              (F.col("o.id") == F.col("f.id")) &
                  # monthly feature is calculated for previous month. 
                  (F.year(F.add_months(F.col("o.date_partition"), -months_to_subtract)) == F.year(F.col("f.date_partition"))) &
                  (F.month(F.add_months(F.col("o.date_partition"), -months_to_subtract)) == F.month(F.col("f.date_partition"))), "left")
            .select("o.*", F.col(f"f.{feature_col_name}").alias(full_col_name))
            .withColumn(full_col_name, F.when(
                (F.year(F.col("converted_to_paid_at")) == F.year(F.col("date_partition"))) &
                (F.month(F.col("converted_to_paid_at")) == F.month(F.col("date_partition"))), 1)
                        .otherwise(F.col(full_col_name)))
    )

    # Some months do not exist in monthly feature_df.
    # Proposal: take previos month (historical)
    result = (
        add_previouse_value_for_feature(result, feature_df, 'date_partition', months_to_subtract, feature_col_name, full_col_name)

        # No previous data. some subscription starts after start date, thus, the first reporting date does not exist as we always look to the previous months.
        .withColumn(full_col_name, F.when(F.col(full_col_name).isNull(), 1).otherwise(F.col(full_col_name)))
        )
    return result

def variance_udf(*cols):
    return float(variance([int(x) for x in cols]))

variance_udf = F.udf(variance_udf, T.FloatType())

def add_half_yearly_and_yearly_variance_features(org_date_partition, feature_df, feature_col_name):
    months = list(range(1, 7)) + [9, 12]
    result = org_date_partition
    for i in months:
        result = add_monthly_feature(org_date_partition=result, feature_df=feature_df, months_to_subtract=i, feature_col_name=feature_col_name)

    columns_6_months = [create_monthly_feature_name(col_name = feature_col_name, number_of_months = i) for i in range(1, 7)]
    columns_year = [create_monthly_feature_name(col_name = feature_col_name, number_of_months = i) for i in range(3, 15, 3)]
    result = (
        result
        .withColumn(f"{feature_col_name}_variance_over_6_months",variance_udf(*[result[col] for col in columns_6_months]))
        .withColumn(f"{feature_col_name}_variance_over_year",variance_udf(*[result[col] for col in columns_year]))
    )
    return result

def add_variance_for_daily_feature(df_with_features_for_variance, feature_col_name, daily_period_list, suffix = ""):
    column_names = [create_daily_feature_name(col_name = feature_col_name, number_of_days = i) for i in daily_period_list]
    return (
        df_with_features_for_variance
        .withColumn(f"{feature_col_name}_variance{suffix}", variance_udf(*[df_with_features_for_variance[col] for col in column_names]))
    )

def mean_of_difference_udf(*cols):
    differences = [cols[i] - cols[i+1] for i in range(len(cols)-1)]
    return float(mean(differences))

mean_of_difference_udf = F.udf(mean_of_difference_udf, T.FloatType())

def add_mean_of_difference_for_daily_feature(df_with_features_for_variance, feature_col_name, daily_period_list, suffix = ""):
    column_names = [create_daily_feature_name(col_name = feature_col_name, number_of_days = i) for i in daily_period_list]
    return (
        df_with_features_for_variance
        .withColumn(f"{feature_col_name}_mean_of_difference{suffix}", mean_of_difference_udf(*[df_with_features_for_variance[col] for col in column_names]))
    )

def add_mean_of_difference_for_monthly_feature(df_with_features_for_variance, feature_col_name, monthly_period_list, suffix = ""):
    column_names = [create_monthly_feature_name(col_name = feature_col_name, number_of_months = i) for i in monthly_period_list]
    return (
        df_with_features_for_variance
        .withColumn(f"{feature_col_name}_mean_of_difference{suffix}", mean_of_difference_udf(*[df_with_features_for_variance[col] for col in column_names]))
    )

