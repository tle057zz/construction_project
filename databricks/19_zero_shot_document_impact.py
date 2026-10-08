# Databricks notebook source
# Zero-shot document-impact classification.
# Asks a Databricks LLM whether each RFI requires a document update.
# The model is not trained on these RFIs.
# Reads digital_engineering.gold.rfi_analytics and does not change that table.
# The label comes from the notes, so the prompt uses the question only.
# Unknown notes stay out of the score.

# COMMAND ----------
import re

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
EXPERIMENT = "rfi_document_impact"
LABEL = "document_update_required"
LABELS = ["Yes", "No"]
ZERO_SHOT_ENDPOINT = "databricks-meta-llama-3-1-8b-instruct"
LOGGED = pd.DataFrame(
    [
        {
            "method": "TF-IDF logistic regression",
            "accuracy": 0.814,
            "precision": 0.808,
            "recall": 0.691,
            "f1": 0.717,
            "yes_recall": 0.421,
        },
        {
            "method": "GTE sentence embedding",
            "accuracy": 0.843,
            "precision": 0.803,
            "recall": 0.793,
            "f1": 0.798,
            "yes_recall": 0.684,
        },
    ]
)

# COMMAND ----------
gold = (
    spark.table(GOLD)
    .select("rfi_id", "question", LABEL)
    .toPandas()
)
gold["question"] = (
    gold["question"].fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
)
gold[LABEL] = gold[LABEL].fillna("").str.strip()
gold = gold[gold["question"].ne("")].copy()
gold = gold.sort_values("rfi_id").reset_index(drop=True)

counts = gold[LABEL].value_counts()
print(f"{len(gold)} RFIs")
print(counts.to_string())

scored = gold[gold[LABEL].isin(LABELS)].copy().reset_index(drop=True)
held_out = gold[~gold[LABEL].isin(LABELS)].copy()
print(f"\nScored {len(scored)} RFIs with Yes or No")
print(scored[LABEL].value_counts().to_string())
if not held_out.empty:
    print(f"\nLeft out: {len(held_out)} RFIs with {LABEL} = Unknown")

spark.createDataFrame(scored[["rfi_id", "question"]]).createOrReplaceTempView(
    "rfi_question_text"
)

# COMMAND ----------
def match_label(text):
    found = "" if text is None else str(text).strip()
    first = re.split(r"\s+", found, maxsplit=1)[0].strip(".,:;\"'") if found else ""
    for label in LABELS:
        if found.lower() == label.lower() or first.lower() == label.lower():
            return label
    return "UNMATCHED"


def score(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "yes_recall": recall_score(y_true, y_pred, pos_label="Yes", zero_division=0),
    }


instruction = (
    "Does this construction RFI require a drawing or specification update? "
    "Reply with only Yes or No."
)
print(f"Classifying questions with {ZERO_SHOT_ENDPOINT}")
classified = spark.sql(
    f"""
    SELECT
        rfi_id,
        ai_query(
            '{ZERO_SHOT_ENDPOINT}',
            concat('{instruction}', '\\n\\nQuestion: ', question)
        ) AS predicted_label
    FROM rfi_question_text
    """
).toPandas()
merged = scored.merge(classified, on="rfi_id", how="left")
predicted = merged["predicted_label"].map(match_label)
unmatched = int((predicted == "UNMATCHED").sum())
if unmatched:
    print(f"{unmatched} replies were not Yes or No.")
    print(merged.loc[predicted == "UNMATCHED", "predicted_label"].head(10).to_string())

metrics = score(merged[LABEL], predicted)
print(f"\nLLM zero-shot, scored once on {len(scored)} RFIs")
print(f"Accuracy   {metrics['accuracy']:.3f}")
print(f"Precision  {metrics['precision']:.3f}")
print(f"Recall     {metrics['recall']:.3f}")
print(f"F1         {metrics['f1']:.3f}")
print(f"Yes recall {metrics['yes_recall']:.3f}")
print()
print(classification_report(merged[LABEL], predicted, labels=LABELS, zero_division=0))
matrix = pd.DataFrame(
    confusion_matrix(merged[LABEL], predicted, labels=LABELS),
    index=[f"actual {label}" for label in LABELS],
    columns=[f"pred {label}" for label in LABELS],
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
    mlflow.log_param("training_text", "question")
    mlflow.log_param("training_set", GOLD)
    mlflow.log_param("target", LABEL)
    mlflow.log_param("rows", len(scored))
    mlflow.log_param("held_out_rows", len(held_out))
    mlflow.log_param("n_splits", 0)
    mlflow.log_param("gte_yes_recall", 0.684)
    for name, value in metrics.items():
        mlflow.log_metric(name, float(value))

print(f"Logged run llama-zero-shot to /Users/{user}/{EXPERIMENT}")
