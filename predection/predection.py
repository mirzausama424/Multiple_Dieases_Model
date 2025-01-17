# from sys import modules
# from fastapi import APIRouter, Depends, HTTPException,Query,Body
# from pydantic import BaseModel
# from typing import List,Any
# from db.database import db_connection
# import pickle
# from datetime import datetime
# import os
# import json
# import numpy as np


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODELS_PATH = os.path.join(BASE_DIR, "../Saved_Models")

# models = {
#     "breast_cancer": pickle.load(open(os.path.join(MODELS_PATH, "breast_cancer_model.sav"), 'rb')),
#     "diabetes": pickle.load(open(os.path.join(MODELS_PATH, "diabetes_model.sav"), 'rb')),
#     "heart_disease": pickle.load(open(os.path.join(MODELS_PATH, "heart_model.sav"), 'rb')),
#     "parkinsons": pickle.load(open(os.path.join(MODELS_PATH, "parkinsons_model.sav"), 'rb'))
# }

# predection_route=APIRouter()

# class predection(BaseModel):
#     model_name:str
#     features:list[Any]

# @predection_route.post(path="/predict")
# async def predict(input_data: predection, user_id: int = Query(...)):
#     # Parse features if they are sent as a string
#     if isinstance(input_data.features, str):
#         try:
#             input_data.features = json.loads(input_data.features)
#         except json.JSONDecodeError:
#             raise HTTPException(status_code=422, detail="Invalid features format. Should be a JSON array.")

#     # Retrieve the model by name
#     model = models.get(input_data.model_name)
#     if not model:
#         raise HTTPException(status_code=404, detail=f"Model '{input_data.model_name}' not found")
    
#     input_data_convert=np.asarray(input_data.features)
#     input_data_reshaped=input_data_convert.reshape(1,-1)
#     # Make the prediction
#     prediction = model.predict(input_data_reshaped)

#     prediction=prediction.tolist()

#     # Save prediction to the database
#     timestamp = datetime.utcnow().isoformat()
#     connection = db_connection()
#     cursor = connection.cursor()
#     try:
#         cursor.execute(
#             """
#             INSERT INTO predictions (user_id, model_name, features, prediction, timestamp)
#             VALUES (?, ?, ?, ?, ?)
#             """,
#             (user_id, input_data.model_name, str(input_data.features), str(prediction), timestamp),
#         )
#         connection.commit()
#     finally:
#         connection.close()

#     return {"model_name": input_data.model_name, "prediction": prediction}

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Any
from db.database import db_connection
import pickle
from datetime import datetime
import os
import json
import numpy as np

# Define base directory and models path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_PATH = os.path.join(BASE_DIR, "../Saved_Models")

# Load models
models = {
   # "breast_cancer": pickle.load(open(os.path.join(MODELS_PATH, "breast_cancer_model.sav"), 'rb')),
    "diabetes": pickle.load(open(os.path.join(MODELS_PATH, "diabetes_model.sav"), 'rb')),
    "heart_disease": pickle.load(open(os.path.join(MODELS_PATH, "heart_model.sav"), 'rb')),
    "parkinsons": pickle.load(open(os.path.join(MODELS_PATH, "parkinsons_model.sav"), 'rb'))
}

# Define the router
predection_route = APIRouter()

# Define input data model
class Predection(BaseModel):
    model_name: str
    features: list[Any]

@predection_route.post(path="/predict")
async def predict(input_data: Predection):
    # Parse features if they are sent as a string
    if isinstance(input_data.features, str):
        try:
            input_data.features = json.loads(input_data.features)
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="Invalid features format. Should be a JSON array.")

    # Retrieve the model by name
    model = models.get(input_data.model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{input_data.model_name}' not found")

    # Prepare features for prediction
    input_data_convert = np.asarray(input_data.features)
    input_data_reshaped = input_data_convert.reshape(1, -1)

    # Make the prediction and get the confidence level (if available)
    if hasattr(model, 'predict_proba'):
        prediction_probabilities = model.predict_proba(input_data_reshaped)
        confidence = max(prediction_probabilities[0])  # Confidence of the predicted class
    else:
        # If model doesn't support predict_proba, use decision_function (SVMs for example)
        decision_values = model.decision_function(input_data_reshaped)
        confidence = np.max(np.abs(decision_values))  # Confidence is based on decision function

    # Get the prediction class
    prediction = model.predict(input_data_reshaped)
    prediction = prediction.tolist()

    # Save prediction to the database (without user_id)
    timestamp = datetime.utcnow().isoformat()
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO predictions (model_name, features, prediction, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (input_data.model_name, str(input_data.features), str(prediction), confidence, timestamp),
        )
        connection.commit()
    finally:
        connection.close()

    # Return prediction and confidence in the response
    return {
        "model_name": input_data.model_name,
        "prediction": prediction,
        "confidence_level": confidence
    }