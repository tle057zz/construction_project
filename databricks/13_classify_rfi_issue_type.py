# Databricks notebook source
# Baseline issue-type classifier.
# Reads digital_engineering.gold.rfi_analytics and does not change that table.
# Question text, plus notes when present, -> TF-IDF -> logistic regression.
# Constructability and Scope Gap each have one RFI, so those two rows are left out of the split.

# COMMAND ----------
import mlflow
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline

GOLD = "digital_engineering.gold.rfi_analytics"
EXPERIMENT = "rfi_issue_type_classification"

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
    lambda row: f"{row['question']} {row['notes']}".strip()
    if row["notes"]
    else row["question"],
    axis=1,
)

counts = gold["issue_type"].value_counts()
print(f"{len(gold)} RFIs")
print(counts.to_string())

held_out = gold[gold["issue_type"].map(counts) < 2].copy()
scored = gold[gold["issue_type"].map(counts) >= 2].copy()
if not held_out.empty:
    print("\nLeft out of cross-validation:")
    print(held_out[["rfi_id", "issue_type"]].to_string(index=False))

label_counts = scored["issue_type"].value_counts()
labels = label_counts.index.tolist()
n_splits = int(label_counts.min())
if n_splits < 2:
    raise SystemExit("Every scored issue type needs at least 2 RFIs.")

# COMMAND ----------
pipeline = Pipeline(
    [
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ]
)
cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
predicted = cross_val_predict(pipeline, scored["model_text"], scored["issue_type"], cv=cv)

accuracy = accuracy_score(scored["issue_type"], predicted)
precision = precision_score(scored["issue_type"], predicted, average="macro", zero_division=0)
recall = recall_score(scored["issue_type"], predicted, average="macro", zero_division=0)
f1 = f1_score(scored["issue_type"], predicted, average="macro", zero_division=0)

print(f"\n{n_splits}-fold stratified CV on {len(scored)} RFIs")
print(f"Accuracy  {accuracy:.3f}")
print(f"Precision {precision:.3f}")
print(f"Recall    {recall:.3f}")
print(f"F1        {f1:.3f}")
print()
print(classification_report(scored["issue_type"], predicted, labels=labels, zero_division=0))
matrix = pd.DataFrame(
    confusion_matrix(scored["issue_type"], predicted, labels=labels),
    index=[f"actual {label}" for label in labels],
    columns=[f"pred {label}" for label in labels],
)
print(matrix.to_string())

# COMMAND ----------
user = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{user}/{EXPERIMENT}")
with mlflow.start_run(run_name="tfidf-logistic-regression"):
    mlflow.log_param("model_type", "Logistic Regression")
    mlflow.log_param("feature_method", "TF-IDF word and bigram")
    mlflow.log_param("training_text", "question plus notes")
    mlflow.log_param("training_set", GOLD)
    mlflow.log_param("rows", len(scored))
    mlflow.log_param("held_out_rows", len(held_out))
    mlflow.log_param("n_splits", n_splits)
    mlflow.log_param("class_weight", "balanced")
    mlflow.log_metric("accuracy", float(accuracy))
    mlflow.log_metric("precision", float(precision))
    mlflow.log_metric("recall", float(recall))
    mlflow.log_metric("f1", float(f1))
    pipeline.fit(scored["model_text"], scored["issue_type"])
    example = scored["model_text"].head(1).to_numpy()
    try:
        mlflow.sklearn.log_model(pipeline, name="model", input_example=example)
    except TypeError:
        mlflow.sklearn.log_model(pipeline, "model", input_example=example)

print(f"Logged run to /Users/{user}/{EXPERIMENT}")
