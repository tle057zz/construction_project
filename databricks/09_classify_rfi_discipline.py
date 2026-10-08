# Databricks notebook source
# Baseline discipline classifier.
# Reads digital_engineering.gold.rfi_analytics and does not change that table.
# Question text -> TF-IDF -> logistic regression.
# Scores come from stratified cross-validation. The smallest discipline has 2 RFIs, so the split is 2-fold.

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
EXPERIMENT = "rfi_discipline_classification"

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

counts = gold["discipline"].value_counts()
print(f"{len(gold)} RFIs")
print(counts.to_string())

n_splits = int(counts.min())
if n_splits < 2:
    raise SystemExit("Every discipline needs at least 2 RFIs for a stratified split.")

# COMMAND ----------
pipeline = Pipeline(
    [
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)),
        (
            "clf",
            LogisticRegression(max_iter=2000, class_weight="balanced"),
        ),
    ]
)
cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
predicted = cross_val_predict(
    pipeline,
    gold["question"],
    gold["discipline"],
    cv=cv,
)

labels = counts.index.tolist()
accuracy = accuracy_score(gold["discipline"], predicted)
precision = precision_score(
    gold["discipline"], predicted, average="macro", zero_division=0
)
recall = recall_score(gold["discipline"], predicted, average="macro", zero_division=0)
f1 = f1_score(gold["discipline"], predicted, average="macro", zero_division=0)

print(f"\n{n_splits}-fold stratified CV on {len(gold)} RFIs")
print(f"Accuracy  {accuracy:.3f}")
print(f"Precision {precision:.3f}")
print(f"Recall    {recall:.3f}")
print(f"F1        {f1:.3f}")
print()
print(classification_report(gold["discipline"], predicted, labels=labels, zero_division=0))
matrix = pd.DataFrame(
    confusion_matrix(gold["discipline"], predicted, labels=labels),
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
    mlflow.log_param("training_set", GOLD)
    mlflow.log_param("rows", len(gold))
    mlflow.log_param("n_splits", n_splits)
    mlflow.log_param("class_weight", "balanced")
    mlflow.log_metric("accuracy", float(accuracy))
    mlflow.log_metric("precision", float(precision))
    mlflow.log_metric("recall", float(recall))
    mlflow.log_metric("f1", float(f1))
    pipeline.fit(gold["question"], gold["discipline"])
    try:
        mlflow.sklearn.log_model(pipeline, name="model")
    except TypeError:
        mlflow.sklearn.log_model(pipeline, "model")

print(f"Logged run to /Users/{user}/{EXPERIMENT}")
