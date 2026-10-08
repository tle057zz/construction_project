# Databricks notebook source
# Compare the issue-type baseline with a GTE embedding classifier.
# If the embedding endpoint is unavailable, score the same text with a zero-shot LLM.
# Reads digital_engineering.gold.rfi_analytics and does not change that table.
# Constructability and Scope Gap each have one RFI, so those two rows stay out of the split.

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
EXPERIMENT = "rfi_issue_type_classification"
EMBEDDING_ENDPOINTS = ("databricks-gte-large-en", "system.ai.gte-large-en")
ZERO_SHOT_ENDPOINT = "databricks-meta-llama-3-1-8b-instruct"

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
    print("\nLeft out of cross-validation:")
    print(held_out[["rfi_id", "issue_type"]].to_string(index=False))

label_counts = scored["issue_type"].value_counts()
labels = label_counts.index.tolist()
n_splits = int(label_counts.min())
if n_splits < 2:
    raise SystemExit("Every scored issue type needs at least 2 RFIs.")

cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
spark.createDataFrame(scored[["rfi_id", "model_text"]]).createOrReplaceTempView(
    "rfi_issue_text"
)

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
    predicted = cross_val_predict(
        pipeline, scored["model_text"], scored["issue_type"], cv=cv
    )
    return predicted, score(scored["issue_type"], predicted)


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
        SELECT rfi_id, ai_query('{endpoint}', model_text) AS embedding
        FROM rfi_issue_text
        """
    ).toPandas()
    merged = scored.merge(embedded, on="rfi_id", how="left").sort_values("rfi_id")
    merged = merged.reset_index(drop=True)
    vectors = np.vstack(merged["embedding"].map(to_vector).to_list())
    predicted = np.empty(len(merged), dtype=object)
    for train_index, test_index in cv.split(vectors, merged["issue_type"]):
        classifier = LogisticRegression(max_iter=2000, class_weight="balanced")
        classifier.fit(vectors[train_index], merged["issue_type"].iloc[train_index])
        predicted[test_index] = classifier.predict(vectors[test_index])
    return predicted, vectors, merged, score(merged["issue_type"], predicted)


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
        "Choose one issue type for this construction RFI. "
        "Reply with only the label. Labels: " + " | ".join(labels)
    )
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
    return predicted.to_numpy(), score(merged["issue_type"], predicted)

# COMMAND ----------
baseline_predicted, baseline_metrics = baseline_predictions()
show_result(
    f"Baseline: TF-IDF logistic regression, {n_splits}-fold stratified CV on {len(scored)} RFIs",
    scored["issue_type"],
    baseline_predicted,
    baseline_metrics,
)

feature_method = ""
run_name = ""
comparison_predicted = None
comparison_metrics = None
embedding_matrix = None
embedding_frame = None
embedding_endpoint = ""
used_zero_shot = False
errors = []

for endpoint in EMBEDDING_ENDPOINTS:
    try:
        (
            comparison_predicted,
            embedding_matrix,
            embedding_frame,
            comparison_metrics,
        ) = embedding_predictions(endpoint)
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
    f"{feature_method}, scored once on {len(scored)} RFIs"
    if used_zero_shot
    else f"{feature_method} plus logistic regression, {n_splits}-fold stratified CV on {len(scored)} RFIs"
)
show_result(title, scored["issue_type"], comparison_predicted, comparison_metrics)

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
    mlflow.log_param("training_text", "question plus notes")
    mlflow.log_param("training_set", GOLD)
    mlflow.log_param("rows", len(scored))
    mlflow.log_param("held_out_rows", len(held_out))
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
        classifier.fit(embedding_matrix, embedding_frame["issue_type"])
        example = embedding_matrix[:1]
        try:
            mlflow.sklearn.log_model(classifier, name="model", input_example=example)
        except TypeError:
            mlflow.sklearn.log_model(classifier, "model", input_example=example)

print(f"Logged run {run_name} to /Users/{user}/{EXPERIMENT}")
if errors and not used_zero_shot:
    print("Earlier embedding attempt:")
    print(errors[0])
