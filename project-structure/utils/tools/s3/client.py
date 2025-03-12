import base64
import hashlib
import io
import os
import pickle
from io import StringIO
from typing import Any, List

import boto3
import pandas as pd


class ClientS3:
    def __init__(self):
        self.resource = boto3.resource("s3")

    def upload_csv(self, bucket: str, key: str, df: pd.DataFrame):
        csv_buffer = StringIO()
        df.to_csv(csv_buffer)
        md = hashlib.md5(csv_buffer.getvalue().encode("utf-8")).digest()
        contents_md5 = base64.b64encode(md).decode("utf-8")
        self.resource.Object(bucket, key).put(Body=csv_buffer.getvalue(), ContentMD5=contents_md5)

    def upload_pickle(self, bucket: str, key: str, data: Any):
        pickle_buffer = pickle.dumps(data)
        self.resource.Object(bucket, key).put(Body=pickle_buffer)

    def download_csvs(self, bucket: str, prefix: str) -> List[pd.DataFrame]:
        lst_df = []
        bucket_ = self.resource.Bucket(bucket)
        for file in bucket_.objects.filter(Prefix=prefix):
            if file.key.endswith(".csv"):
                body = file.get()["Body"].read()
                df = pd.read_csv(io.BytesIO(body), encoding="utf8")
                lst_df.append(df)
        return lst_df

    def download_pickles(self, bucket: str, prefix: str) -> List[pd.DataFrame]:
        lst_df = []
        bucket_ = self.resource.Bucket(bucket)
        for file in bucket_.objects.filter(Prefix=prefix):
            if file.key.endswith(".pkl"):
                body = file.get()["Body"].read()
                df = pickle.loads(body)
                lst_df.append(df)
        return lst_df

    def upload_png(self, bucket: str, key: str, fig: bytes):
        png_buffer = io.BytesIO(fig)
        self.resource.Object(bucket, key).put(Body=png_buffer.getvalue(), ContentType="image/png")

    def copy_csv(self, source_key: str, source_bucket: str, key: str, bucket: str):
        self.resource.Object(bucket, key).copy_from(CopySource=source_bucket + "/" + source_key)

    def list_objects(self, bucket: str, prefix: str) -> List[str]:
        lst_df_names = []
        bucket_ = self.resource.Bucket(bucket)
        for file in bucket_.objects.filter(Prefix=prefix):
            lst_df_names.append(file.key)
        return lst_df_names

    def download_dir(self, bucket: str, path: str, output_root: str = "") -> None:
        """
        Downloads directory from the S3, keeping the same paths
        """
        s3_path = "/".join([p for p in path.split("/") if p])
        bucket_ = self.resource.Bucket(bucket)
        for obj in bucket_.objects.filter(Prefix=s3_path):
            # Filter out empty and directory objects.
            if obj.size > 0 and not obj.key.endswith("/"):
                local_path = os.path.join(output_root, obj.key)
                if os.path.exists(local_path):
                    continue
                dir_path = os.path.dirname(local_path)
                os.makedirs(dir_path, exist_ok=True)
                bucket_.download_file(obj.key, local_path)

    def spark_write_df(self,
        df,
        path,
        parts_count=16,
        write_mode='overwrite',
        write_format='parquet',
        parts_col= None
    ):
        """Unified function to write back spark dataframes to s3
            This function handles all write modes, formats and partitioning in one place.
            
            Arguments:
                df (pyspark.dataframe) : the dataframe to be written
                path (string)          : the s3 path to write to 
                parts_count (int)      : number of files to write in. if writing by partition, this will be the number of files per partition
                write_mode (string)    : spark write mode, supports "overwrite", "append", or "insert". 
                                        insert is only possible if writing by partition, and behaves as an INSERT OVERWRITE in SQL
                write_format (string)  : data format to write it, supports usual spark formats like "orc", "parquet", etc
                parts_col (string)     : column name to use to write by partition, if specified
            
            Returns:
                None
        """
        
        if parts_col is None:
            (df.repartition(parts_count)
            .write.mode(write_mode).format(write_format).save(path)
            )
            
        else:
            if write_mode=='insert':
                spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
                
                (df.repartition(parts_count)
                .write.mode('overwrite').partitionBy(parts_col).format(write_format).save(path)
                )
                spark.conf.set("spark.sql.sources.partitionOverwriteMode", "static") #restoring default
                
                
            else:
                (df.repartition(parts_count)
                .write.mode(write_mode).partitionBy(parts_col).format(write_format).save(path)
                )
                
        print(f"Dataset is saved at {path}")
        return 
