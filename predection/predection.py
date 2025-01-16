from sys import modules
from fastapi import APIRouter, Depends, HTTPException,Query,Body
from pydantic import BaseModel
from typing import List,Any
from db.database import db_connection
import pickle
from datetime import datetime
import os
import json
import numpy as np


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_PATH = os.path.join(BASE_DIR, "../Saved_Models")

models = {
    "breast_cancer": pickle.load(open(os.path.join(MODELS_PATH, "breast_cancer_model.sav"), 'rb')),
    "diabetes": pickle.load(open(os.path.join(MODELS_PATH, "diabetes_model.sav"), 'rb')),
    "heart_disease": pickle.load(open(os.path.join(MODELS_PATH, "heart_model.sav"), 'rb')),
    "parkinsons": pickle.load(open(os.path.join(MODELS_PATH, "parkinsons_model.sav"), 'rb'))
}

predection_route=APIRouter()

class predection(BaseModel):
    model_name:str
    features:list[Any]

@predection_route.post(path="/predict")
async def predict(input_data: predection, user_id: int = Query(...)):
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
    
    input_data_convert=np.asarray(input_data.features)
    input_data_reshaped=input_data_convert.reshape(1,-1)
    # Make the prediction
    prediction = model.predict(input_data_reshaped)

    prediction=prediction.tolist()

    # Save prediction to the database
    timestamp = datetime.utcnow().isoformat()
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO predictions (user_id, model_name, features, prediction, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, input_data.model_name, str(input_data.features), str(prediction), timestamp),
        )
        connection.commit()
    finally:
        connection.close()

    return {"model_name": input_data.model_name, "prediction": prediction}