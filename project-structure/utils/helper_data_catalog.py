# Databricks notebook source
from datetime import datetime, timedelta

# COMMAND ----------

# DATES for churn

# RUNDATE is a day when algorithm runs and predicts customers churning in X days. 
RUNDATE = datetime.now().strftime("%Y-%m-%d") # hardcoded for training: datetime.strptime('2024-07-01', "%Y-%m-%d") 
DAYS_90 = 90 # 90 days is used to calculate last date partition - it should be 90 days before and training will be on last date partition + 89
DAYS_BEFORE_CHURN = DAYS_90
DAYS_89 = 89 # prediction is made 90-1 days before, because we do not have data on the day the algorithm is running
PREDICT_X_DAYS_BEFORE_CHURN = DAYS_89

RUNDATE_MINUS_DAYS_BEFORE_CHURN = (RUNDATE - timedelta(days=DAYS_90)).strftime("%Y-%m-%d")

START_DATE_CHURN_DATE = (RUNDATE - timedelta(days=365 * 3 + 1))
START_DATE_CHURN = START_DATE_CHURN_DATE.strftime("%Y-%m-%d") # start with data 3 years ago.
START_DATE_MINUS_1_YEAR = START_DATE_CHURN_DATE - timedelta(days=365 + 1)
DATE_PARTITION_INTERVAL = "interval 1 month" # "interval 1 week" # "interval 1 month"

TARGET_NAME = f"is_churned_next_{DAYS_BEFORE_CHURN}_days"

MONTHLY_6_IN_DAYS_ARRAY = [30, 60, 90, 121, 151, 182]
QUARTERLY_STEPS_1_YEAR_IN_DAYS_ARRAY = [90, 182, 273, 364]

MONTHLY_6_AND_QUARTERLY_1_YEAR_ARRAY = MONTHLY_6_IN_DAYS_ARRAY +  [273, 364]

MONTHLY_6_IN_MONTHS_RANGE = range(1, 7)
QUARTERLY_IN_MONTHS_RANGE = range(3, 15, 3)

# COMMAND ----------

# S3 Bucket Paths

S3_BUCKET = 'data-science-data'
PROJECT_NAME = 'CHURN_PREDICTION'
GENERAL_DATA_PATH = (
  's3://' +
  f'{S3_BUCKET}/{PROJECT_NAME}/data/' +
  f'rundate_{RUNDATE_MINUS_DAYS_BEFORE_CHURN}/' +
  f'startdate_{START_DATE_CHURN}'
)

# Output Paths

# raw data

# target
raw_data_for_target_raw_path = f'{GENERAL_DATA_PATH}/raw_data/01_raw_data_for_target'

# features
raw_data_for_feature_one_path = f'{GENERAL_DATA_PATH}/raw_data/01_raw_data_for_feature_one_path'
raw_data_for_feature_two_path = f'{GENERAL_DATA_PATH}/raw_data/02_raw_data_for_feature_two_path'

# # intermediate data

# # target
# # churn_data_sequenced_path = f'{GENERAL_DATA_PATH}/intermediate_data/01_churn_data_sequenced'

# # features
churn_feature_one_sequenced_path = f'{GENERAL_DATA_PATH}/intermediate_data/01_churn_feature_one_sequenced_path'

# # feature transformations
churn_imputed_nulls_sequenced_path = f'{GENERAL_DATA_PATH}/intermediate_data/churn_imputed_nulls_sequenced_path'

# # final data

# # target
churn_data_w_labels_full_path = f'{GENERAL_DATA_PATH}/master_data/churn_data_w_labels_full'
ids_train_test_split_path = f'{GENERAL_DATA_PATH}/master_data/ids_train_test_split_path'
ids_train_validation_split_path = f'{GENERAL_DATA_PATH}/master_data/ids_train_validation_split_path'

churn_data_w_features_labels_path = f'{GENERAL_DATA_PATH}/master_data/churn_data_w_features_labels_2'
churn_data_w_features_labels_previous_path = f'{GENERAL_DATA_PATH}/master_data/churn_data_w_features_labels'

# # test and train
train_path = f'{GENERAL_DATA_PATH}/master_data/train_path'
validation_path = f'{GENERAL_DATA_PATH}/master_data/validation_path'
test_path = f'{GENERAL_DATA_PATH}/master_data/test_path'
# # prediction
predicted_churned_ids_path = f'{GENERAL_DATA_PATH}/master_data/predicted_churned_ids_path'
