# Databricks notebook source
# Zero-shot issue-type classification.
# Asks a Databricks LLM to choose one issue type for each RFI.
# The model is not trained on these RFIs.
# Reads digital_engineering.gold.rfi_analytics and does not change that table.
# Constructability and Scope Gap each have one RFI, so those two rows stay out of the score.

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
EXPERIMENT = "rfi_issue_type_classification"
ZERO_SHOT_ENDPOINT = "databricks-meta-llama-3-1-8b-instruct"
LOGGED = pd.DataFrame(
    [
        {
            "method": "TF-IDF logistic regression",
            "accuracy": 0.695,
            "precision": 0.522,
            "recall": 0.297,
            "f1": 0.336,
        },
        {
            "method": "GTE sentence embedding",
            "accuracy": 0.724,
            "precision": 0.623,
            "recall": 0.409,
            "f1": 0.468,
        },
    ]
)

# COMMAND ----------
gold = (
    spark.table(GOLD)
    .select("rfi_id", "question", "notes", "issue_type")
    .toPandas()
)
gold["question"] = (
    gold["question"].fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
)
gold["notes"] = gold["notes"].fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
gold["issue_type"] = gold["issue_type"].fillna("").str.strip()
gold = gold[gold["question"].ne("") & gold["issue_type"].ne("")].copy()
gold["model_text"] = gold.apply(
    lambda row: f"{row['question']} {row['notes']}".strip() if row["notes"] else row["question"],
    axis=1,
)
gold = gold.sort_values("rfi_id").reset_index(drop=True)

counts = gold["issue_type"].value_counts()
print(f"{len(gold)} RFIs")
print(counts.to_string())

held_out = gold[gold["issue_type"].map(counts) < 2].copy()
scored = gold[gold["issue_type"].map(counts) >= 2].copy().reset_index(drop=True)
if not held_out.empty:
    print("\nLeft out of the score:")
    print(held_out[["rfi_id", "issue_type"]].to_string(index=False))

labels = scored["issue_type"].value_counts().index.tolist()
spark.createDataFrame(scored[["rfi_id", "model_text"]]).createOrReplaceTempView(
    "rfi_issue_text"
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
    "Choose one issue type for this construction RFI. "
    "Reply with only the label. Labels: " + " | ".join(labels)
)
print(f"Classifying questions with {ZERO_SHOT_ENDPOINT}")
classified = spark.sql(
    f"""
    SELECT
        rfi_id,
        ai_query(
            '{ZERO_SHOT_ENDPOINT}',
            concat('{instruction}', '\\n\\nQuestion: ', model_text)
        ) AS predicted_issue_type
    FROM rfi_issue_text
    """
).toPandas()
merged = scored.merge(classified, on="rfi_id", how="left")
predicted = merged["predicted_issue_type"].map(match_label)
unmatched = int((predicted == "UNMATCHED").sum())
if unmatched:
    print(f"{unmatched} replies did not name an issue-type label.")
    print(merged.loc[predicted == "UNMATCHED", "predicted_issue_type"].head(10).to_string())

metrics = score(merged["issue_type"], predicted)
print(f"\nLLM zero-shot, scored once on {len(scored)} RFIs")
print(f"Accuracy  {metrics['accuracy']:.3f}")
print(f"Precision {metrics['precision']:.3f}")
print(f"Recall    {metrics['recall']:.3f}")
print(f"F1        {metrics['f1']:.3f}")
print()
print(classification_report(merged["issue_type"], predicted, labels=labels, zero_division=0))
matrix = pd.DataFrame(
    confusion_matrix(merged["issue_type"], predicted, labels=labels),
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
    mlflow.log_param("training_text", "question plus notes")
    mlflow.log_param("training_set", GOLD)
    mlflow.log_param("rows", len(scored))
    mlflow.log_param("held_out_rows", len(held_out))
    mlflow.log_param("n_splits", 0)
    mlflow.log_param("gte_f1", 0.468)
    for name, value in metrics.items():
        mlflow.log_metric(name, float(value))

print(f"Logged run llama-zero-shot to /Users/{user}/{EXPERIMENT}")
