# Databricks notebook source
import pyspark.sql.functions as F
import matplotlib.pyplot as plt

# COMMAND ----------

def d(df):
    return df.limit(10).display()

# COMMAND ----------

def null_ratio(df, col_name):
    nulls = df.where(F.col(col_name).isNull()).count()
    print(f"{col_name} nulls: {nulls}")

# COMMAND ----------

def plot_hist(df, col_name):
    col = df.select(col_name).rdd.flatMap(lambda x: x).collect()

    # Plotting the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(col, bins=20, color='blue', edgecolor='black')  # Adjust bins as necessary
    plt.title('Histogram of Column Values')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()

# COMMAND ----------

def n(df):
    return df.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df.columns]).display()
