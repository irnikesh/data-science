from pyspark.sql import SparkSession, DataFrame
from typing import Any, Dict, List
import pyspark.sql.functions as F

spark = SparkSession.builder.appName("Modeling").getOrCreate()

# ================================================================================= #
# Perform Target Encoding :
# ================================================================================= #

def compute_target_encoder(master_data: DataFrame, char_columns: List[str], target_feature: str) -> Dict[str, Any]:
    """Function to compute imputation values for numeric columns based on chosen method (mean or median)
    """
    glob_avg_targ = master_data.select(F.mean(target_feature)).collect()[0][0]
    encode_dict = {}
    encode_dict["_global_average"] = glob_avg_targ

    for char in char_columns:
        enc_name = f"{char}_{target_feature}"
        print(f"Creating encoding for {char} as {enc_name}")
        encode_dict[char] = (
            master_data.groupBy(char)
            .agg(F.mean(target_feature).alias(enc_name))
            .toPandas()
            .set_index(char)[enc_name]
            .to_dict()
        )
    return encode_dict


def perform_target_encoding(
    master_data: DataFrame, target_encoder, char_columns: List[str], target_feature: str
) -> DataFrame:
    glob_avg_targ = target_encoder.get("_global_average")
    spark = SparkSession.builder.getOrCreate()

    for char in char_columns:
        enc_name = f"{char}_{target_feature}"
        print(f"Applying saved encoding for {char} as {enc_name}")

        lkup = spark.createDataFrame(target_encoder.get(char).items(), [char, enc_name])
        master_data = master_data.join(lkup, char, "left").fillna(glob_avg_targ, subset=[enc_name])
        master_data = master_data.drop(char).withColumnRenamed(enc_name, char)

    print(f"Encoded data: {master_data.cache().count()} rows and {len(master_data.columns)} columns")
    return master_data
