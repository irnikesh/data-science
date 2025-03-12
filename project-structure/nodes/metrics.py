# Databricks notebook source
from sklearn.metrics import (
    recall_score, roc_auc_score, precision_score, f1_score,
    confusion_matrix, ConfusionMatrixDisplay
)
import pandas as pd
import matplotlib.pyplot as plt

# COMMAND ----------

def plot_confusion_matrix(y_true, y_pred):
        
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[0, 1])

    disp.plot(cmap='Blues', values_format='d')
    # disp.im_.colorbar.ax.patches[0].set_facecolor('blue')
    # disp.im_.colorbar.ax.patches[1].set_facecolor('white')
    plt.title('Confusion matrix')
    plt.show()

# COMMAND ----------

def tracking_evaluation_metric(X_test, y_test, modl, model_name = "lR_weight"):
    
    y_pred_proba = modl.predict_proba(X_test)[:, 1]
    y_pred = modl.predict(X_test)
    recall,roc_auc,precision, f1 =[],[],[],[]

    recall.append(round(recall_score(y_test, y_pred),4))
    roc_auc.append(round(roc_auc_score(y_test, y_pred_proba),4))
    precision.append(round(precision_score(y_test, y_pred),4))
    f1.append(round(f1_score(y_test, y_pred, average='weighted'),4))

    model_names = [model_name]
    result_df = pd.DataFrame({'Recall':recall, 'Roc_Auc':roc_auc, 'Precision':precision, 'F1':f1}, index=model_names)
    plot_confusion_matrix(y_test, y_pred)
    
    return result_df

# COMMAND ----------

