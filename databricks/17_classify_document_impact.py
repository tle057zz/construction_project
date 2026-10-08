# Databricks notebook source
# Baseline document-impact classifier.
# Reads digital_engineering.gold.rfi_analytics and does not change that table.
# The label comes from the notes, so the model reads the question only.
# Unknown notes stay out. Yes and No are scored with TF-IDF and logistic regression.

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
EXPERIMENT = "rfi_document_impact"
LABEL = "document_update_required"
LABELS = ["Yes", "No"]

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

yes_count = int((scored[LABEL] == "Yes").sum())
n_splits = 5 if yes_count >= 5 else int(yes_count)
if n_splits < 2:
    raise SystemExit("Yes needs at least 2 RFIs for a stratified split.")

# COMMAND ----------
pipeline = Pipeline(
    [
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ]
)
cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
predicted = cross_val_predict(pipeline, scored["question"], scored[LABEL], cv=cv)

accuracy = accuracy_score(scored[LABEL], predicted)
precision = precision_score(scored[LABEL], predicted, average="macro", zero_division=0)
recall = recall_score(scored[LABEL], predicted, average="macro", zero_division=0)
f1 = f1_score(scored[LABEL], predicted, average="macro", zero_division=0)
yes_recall = recall_score(scored[LABEL], predicted, pos_label="Yes", zero_division=0)

print(f"\n{n_splits}-fold stratified CV on {len(scored)} RFIs")
print(f"Accuracy   {accuracy:.3f}")
print(f"Precision  {precision:.3f}")
print(f"Recall     {recall:.3f}")
print(f"F1         {f1:.3f}")
print(f"Yes recall {yes_recall:.3f}")
print()
print(classification_report(scored[LABEL], predicted, labels=LABELS, zero_division=0))
matrix = pd.DataFrame(
    confusion_matrix(scored[LABEL], predicted, labels=LABELS),
    index=[f"actual {label}" for label in LABELS],
    columns=[f"pred {label}" for label in LABELS],
)
print(matrix.to_string())

# COMMAND ----------
user = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{user}/{EXPERIMENT}")
with mlflow.start_run(run_name="tfidf-logistic-regression"):
    mlflow.log_param("model_type", "Logistic Regression")
    mlflow.log_param("feature_method", "TF-IDF word and bigram")
    mlflow.log_param("training_text", "question")
    mlflow.log_param("training_set", GOLD)
    mlflow.log_param("target", LABEL)
    mlflow.log_param("rows", len(scored))
    mlflow.log_param("held_out_rows", len(held_out))
    mlflow.log_param("n_splits", n_splits)
    mlflow.log_param("class_weight", "balanced")
    mlflow.log_metric("accuracy", float(accuracy))
    mlflow.log_metric("precision", float(precision))
    mlflow.log_metric("recall", float(recall))
    mlflow.log_metric("f1", float(f1))
    mlflow.log_metric("yes_recall", float(yes_recall))
    pipeline.fit(scored["question"], scored[LABEL])
    example = scored["question"].head(1).to_numpy()
    try:
        mlflow.sklearn.log_model(pipeline, name="model", input_example=example)
    except TypeError:
        mlflow.sklearn.log_model(pipeline, "model", input_example=example)

print(f"Logged run to /Users/{user}/{EXPERIMENT}")
