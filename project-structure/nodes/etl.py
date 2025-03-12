import pyspark.sql.functions as F
import pyspark.sql.types as T

def apply_split_train_test(
    df_train_test_ids, # df with train & test flags for given IDs
    df_master_data, # df with master data (targets & features)
    keys_list = ['organization_id']
    ):
    df_train = (
        df_master_data
        .join(df_train_test_ids.where(F.col('is_train')==True), keys_list, 'inner')
        .drop('is_train')
    )
    df_test = (
        df_master_data
        .join(df_train_test_ids.where(F.col('is_train')==False), keys_list, 'inner')
        .drop('is_train')
    )
    return df_train, df_test


def split_features_target(df, features_list, target_col):
    X = df[features_list]
    y = df[target_col]
    return X, y

def convert_long_to_int(df):
    for col, dtype in df.dtypes:
        if dtype == "long" or dtype == "bigint":
            df = df.withColumn(col, F.col(col).cast(T.IntegerType()))
    return df


def convert_double_to_float(df):
    for col, dtype in df.dtypes:
        if dtype == "double" or "decimal" in dtype:
            df = df.withColumn(col, F.round(F.col(col).cast(T.FloatType()),2))
            
    return df

def convert_df_toPandas(df):
    return convert_double_to_float(convert_long_to_int(df)).toPandas()
