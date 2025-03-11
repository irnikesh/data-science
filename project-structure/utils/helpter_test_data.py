import pyspark.sql.functions as F
import pyspark.sql.types as T
from databricks.sdk.runtime import spark

# create data sets for testing 

def create_test_data():
    data_1 = [
        ('1', '2022-07-01', 100.0, None, '0', 'plan', False, True, 0.5, 'id'),
        ('2', '2022-07-01', 100.0, None, '0', 'plan', False, True, 0.5, 'id'),
        ('3', '2023-01-01', 100.0, None, 0.0, 'plan', False, True, 0.5, 'id'),
    ]
    columns = ["id", "date_partition", "total_dollars", "churn_type", "change_dollars", "plan", "is_monthly", "is_yearly", "occupancy_rate", "customer_id"]
    output = ( 
                spark.createDataFrame(data_1, columns)
                .withColumn("date_partition", F.col("date_partition").cast(T.DateType()))
    )

    return output
