# Databricks notebook source
# Zero-shot discipline classification.
# Asks a Databricks LLM to choose one discipline for each RFI question.
# The model is not trained on these RFIs.
# Reads digital_engineering.gold.rfi_analytics and does not change that table.

# COMMAND ----------
import mlflow
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

GOLD = "digital_engineering.gold.rfi_analytics"
EXPERIMENT = "rfi_discipline_classification"
ZERO_SHOT_ENDPOINT = "databricks-meta-llama-3-1-8b-instruct"
LOGGED = pd.DataFrame(
    [
        {
            "method": "TF-IDF logistic regression",
            "accuracy": 0.645,
            "precision": 0.536,
            "recall": 0.428,
            "f1": 0.456,
        },
        {
            "method": "GTE sentence embedding",
            "accuracy": 0.701,
            "precision": 0.557,
            "recall": 0.467,
            "f1": 0.496,
        },
    ]
)

# COMMAND ----------
gold = (
    spark.table(GOLD)
    .select("rfi_id", "question", "discipline")
    .toPandas()
)
gold["question"] = (
    gold["question"].fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
)
gold["discipline"] = gold["discipline"].fillna("").str.strip()
gold = gold[gold["question"].ne("") & gold["discipline"].ne("")].copy()
gold = gold.sort_values("rfi_id").reset_index(drop=True)

counts = gold["discipline"].value_counts()
labels = counts.index.tolist()
print(f"{len(gold)} RFIs")
print(counts.to_string())

spark.createDataFrame(gold[["rfi_id", "question"]]).createOrReplaceTempView(
    "rfi_question_text"
)

# COMMAND ----------
def match_label(text):
    found = "" if text is None else str(text).strip()
    for label in labels:
        if found.lower() == label.lower():
            return label
    for label in sorted(labels, key=len, reverse=True):
        if label.lower() in found.lower():
            return label
    return "UNMATCHED"


def score(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
    }


instruction = (
    "Choose one engineering discipline for this construction RFI. "
    "Reply with only the label. Labels: " + " | ".join(labels)
)
print(f"Classifying questions with {ZERO_SHOT_ENDPOINT}")
classified = spark.sql(
    f"""
    SELECT
        rfi_id,
        ai_query(
            '{ZERO_SHOT_ENDPOINT}',
            concat('{instruction}', '\\n\\nQuestion: ', question)
        ) AS predicted_discipline
    FROM rfi_question_text
    """
).toPandas()
merged = gold.merge(classified, on="rfi_id", how="left")
predicted = merged["predicted_discipline"].map(match_label)
unmatched = int((predicted == "UNMATCHED").sum())
if unmatched:
    print(f"{unmatched} replies did not name a discipline label.")
    print(merged.loc[predicted == "UNMATCHED", "predicted_discipline"].head(10).to_string())

metrics = score(merged["discipline"], predicted)
print("\nLLM zero-shot, scored once")
print(f"Accuracy  {metrics['accuracy']:.3f}")
print(f"Precision {metrics['precision']:.3f}")
print(f"Recall    {metrics['recall']:.3f}")
print(f"F1        {metrics['f1']:.3f}")
print()
print(classification_report(merged["discipline"], predicted, labels=labels, zero_division=0))
matrix = pd.DataFrame(
    confusion_matrix(merged["discipline"], predicted, labels=labels),
    index=[f"actual {label}" for label in labels],
    columns=[f"pred {label}" for label in labels],
)
print(matrix.to_string())

comparison = pd.concat(
    [LOGGED, pd.DataFrame([{"method": "LLM zero-shot", **metrics}])],
    ignore_index=True,
)
print()
print(comparison.to_string(index=False, float_format=lambda value: f"{value:.3f}"))

# COMMAND ----------
user = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{user}/{EXPERIMENT}")
with mlflow.start_run(run_name="llama-zero-shot"):
    mlflow.log_param("model_type", "Zero-shot")
    mlflow.log_param("feature_method", "LLM zero-shot")
    mlflow.log_param("llm_endpoint", ZERO_SHOT_ENDPOINT)
    mlflow.log_param("training_set", GOLD)
    mlflow.log_param("rows", len(gold))
    mlflow.log_param("n_splits", 0)
    mlflow.log_param("gte_f1", 0.496)
    for name, value in metrics.items():
        mlflow.log_metric(name, float(value))

print(f"Logged run llama-zero-shot to /Users/{user}/{EXPERIMENT}")
