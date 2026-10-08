# Databricks notebook source
# Compare the discipline baseline with a GTE embedding classifier.
# If the embedding endpoint is unavailable, score the same questions with a zero-shot LLM.
# Reads digital_engineering.gold.rfi_analytics and does not change that table.

# COMMAND ----------
import json

import mlflow
import numpy as np
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
EMBEDDING_ENDPOINTS = ("databricks-gte-large-en", "system.ai.gte-large-en")
ZERO_SHOT_ENDPOINT = "databricks-meta-llama-3-1-8b-instruct"

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

n_splits = int(counts.min())
if n_splits < 2:
    raise SystemExit("Every discipline needs at least 2 RFIs for a stratified split.")

cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
questions = spark.createDataFrame(gold[["rfi_id", "question"]])
questions.createOrReplaceTempView("rfi_question_text")

# COMMAND ----------
def score(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
    }


def show_result(title, y_true, y_pred, metrics):
    print(f"\n{title}")
    print(f"Accuracy  {metrics['accuracy']:.3f}")
    print(f"Precision {metrics['precision']:.3f}")
    print(f"Recall    {metrics['recall']:.3f}")
    print(f"F1        {metrics['f1']:.3f}")
    print()
    print(classification_report(y_true, y_pred, labels=labels, zero_division=0))
    matrix = pd.DataFrame(
        confusion_matrix(y_true, y_pred, labels=labels),
        index=[f"actual {label}" for label in labels],
        columns=[f"pred {label}" for label in labels],
    )
    print(matrix.to_string())


def baseline_predictions():
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ]
    )
    predicted = cross_val_predict(pipeline, gold["question"], gold["discipline"], cv=cv)
    return predicted, score(gold["discipline"], predicted)


def to_vector(value):
    if value is None:
        raise ValueError("The embedding endpoint returned a null vector.")
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, str):
        value = json.loads(value)
    array = np.asarray(value, dtype=float)
    if array.ndim != 1 or array.size < 8:
        raise ValueError(f"Unexpected embedding shape {array.shape}.")
    return array


def embedding_predictions(endpoint):
    print(f"Embedding questions with {endpoint}")
    embedded = spark.sql(
        f"""
        SELECT rfi_id, ai_query('{endpoint}', question) AS embedding
        FROM rfi_question_text
        """
    ).toPandas()
    merged = gold.merge(embedded, on="rfi_id", how="left")
    vectors = np.vstack(merged["embedding"].map(to_vector).to_list())
    predicted = np.empty(len(merged), dtype=object)
    for train_index, test_index in cv.split(vectors, merged["discipline"]):
        classifier = LogisticRegression(max_iter=2000, class_weight="balanced")
        classifier.fit(vectors[train_index], merged["discipline"].iloc[train_index])
        predicted[test_index] = classifier.predict(vectors[test_index])
    return predicted, vectors, score(merged["discipline"], predicted)


def match_label(text):
    found = "" if text is None else str(text).strip()
    for label in labels:
        if found.lower() == label.lower():
            return label
    for label in sorted(labels, key=len, reverse=True):
        if label.lower() in found.lower():
            return label
    return "UNMATCHED"


def zero_shot_predictions():
    print(f"Classifying questions with {ZERO_SHOT_ENDPOINT}")
    instruction = (
        "Choose one engineering discipline for this construction RFI. "
        "Reply with only the label. Labels: " + " | ".join(labels)
    )
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
    return predicted.to_numpy(), score(merged["discipline"], predicted)

# COMMAND ----------
baseline_predicted, baseline_metrics = baseline_predictions()
show_result(
    f"Baseline: TF-IDF logistic regression, {n_splits}-fold stratified CV",
    gold["discipline"],
    baseline_predicted,
    baseline_metrics,
)

feature_method = ""
run_name = ""
comparison_predicted = None
comparison_metrics = None
embedding_matrix = None
embedding_endpoint = ""
used_zero_shot = False
errors = []

for endpoint in EMBEDDING_ENDPOINTS:
    try:
        comparison_predicted, embedding_matrix, comparison_metrics = embedding_predictions(endpoint)
        embedding_endpoint = endpoint
        feature_method = "GTE sentence embedding"
        run_name = "gte-embedding-logistic-regression"
        break
    except Exception as error:
        errors.append(f"{endpoint}: {error}")
        print(f"{endpoint} did not return embeddings.")
        print(error)

if comparison_predicted is None:
    used_zero_shot = True
    comparison_predicted, comparison_metrics = zero_shot_predictions()
    feature_method = "LLM zero-shot"
    run_name = "llama-zero-shot"

title = (
    f"{feature_method}, scored once"
    if used_zero_shot
    else f"{feature_method} plus logistic regression, {n_splits}-fold stratified CV"
)
show_result(title, gold["discipline"], comparison_predicted, comparison_metrics)

comparison = pd.DataFrame(
    [
        {"method": "TF-IDF logistic regression", **baseline_metrics},
        {"method": feature_method, **comparison_metrics},
    ]
)
print()
print(comparison.to_string(index=False, float_format=lambda value: f"{value:.3f}"))

# COMMAND ----------
user = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{user}/{EXPERIMENT}")
with mlflow.start_run(run_name=run_name):
    mlflow.log_param("model_type", "Zero-shot" if used_zero_shot else "Logistic Regression")
    mlflow.log_param("feature_method", feature_method)
    mlflow.log_param("training_set", GOLD)
    mlflow.log_param("rows", len(gold))
    mlflow.log_param("n_splits", 0 if used_zero_shot else n_splits)
    mlflow.log_param("baseline_f1", float(baseline_metrics["f1"]))
    if embedding_endpoint:
        mlflow.log_param("embedding_endpoint", embedding_endpoint)
    if used_zero_shot:
        mlflow.log_param("llm_endpoint", ZERO_SHOT_ENDPOINT)
    for name, value in comparison_metrics.items():
        mlflow.log_metric(name, float(value))
    if embedding_matrix is not None:
        classifier = LogisticRegression(max_iter=2000, class_weight="balanced")
        classifier.fit(embedding_matrix, gold["discipline"])
        example = embedding_matrix[:1]
        try:
            mlflow.sklearn.log_model(classifier, name="model", input_example=example)
        except TypeError:
            mlflow.sklearn.log_model(classifier, "model", input_example=example)

print(f"Logged run {run_name} to /Users/{user}/{EXPERIMENT}")
if errors and not used_zero_shot:
    print("Earlier embedding attempt:")
    print(errors[0])
