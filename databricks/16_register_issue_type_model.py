# Databricks notebook source
# Register the GTE issue-type classifier in Unity Catalog.
# The logged model scores an embedding vector, not the raw question text.
# It does not change the RFI tables.

# COMMAND ----------
import mlflow

EXPERIMENT = "rfi_issue_type_classification"
REGISTERED_NAME = "digital_engineering.ml.rfi_issue_type_classifier"
KNOWN_MODEL_ID = "m-43878015bbd24190af31b590f825d6c8"
RUN_NAME = "gte-embedding-logistic-regression"

mlflow.set_registry_uri("databricks-uc")

# COMMAND ----------
def logged_model_uri():
    user = spark.sql("SELECT current_user()").first()[0]
    experiment = mlflow.get_experiment_by_name(f"/Users/{user}/{EXPERIMENT}")
    if experiment is None:
        print(f"Experiment not found. Using logged model {KNOWN_MODEL_ID}.")
        return f"models:/{KNOWN_MODEL_ID}"
    try:
        found = mlflow.search_logged_models(experiment_ids=[experiment.experiment_id])
    except Exception as error:
        print(f"Could not list logged models: {error}")
        return f"models:/{KNOWN_MODEL_ID}"
    records = found.to_dict("records") if hasattr(found, "to_dict") else list(found)
    for record in records:
        text = " ".join(str(value) for value in record.values())
        model_id = record.get("model_id") or record.get("id")
        if model_id and (RUN_NAME in text or record.get("name") == RUN_NAME):
            print(f"Found {RUN_NAME}: {model_id}")
            return f"models:/{model_id}"
    print(f"Using logged model {KNOWN_MODEL_ID}.")
    return f"models:/{KNOWN_MODEL_ID}"


model_uri = logged_model_uri()
registered = mlflow.register_model(model_uri, REGISTERED_NAME)
print(f"Registered {registered.name} version {registered.version}")

client = mlflow.MlflowClient(registry_uri="databricks-uc")
client.set_registered_model_alias(REGISTERED_NAME, "champion", registered.version)
client.update_registered_model(
    REGISTERED_NAME,
    description=(
        "GTE sentence embedding plus logistic regression for RFI issue type. "
        "Accuracy 0.72 and macro F1 0.47 on 105 RFIs. "
        "Constructability and Scope Gap were left out of that score. "
        "The model input is the embedding vector from databricks-gte-large-en, "
        "not the raw question and notes."
    ),
)
print(f"Alias champion -> version {registered.version}")
print("Input: one embedding vector from databricks-gte-large-en.")
print(f"Catalog path: {REGISTERED_NAME}")
