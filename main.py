from fastapi import FastAPI
import uvicorn
from Auth.auth import auth_router
from predection.predection import predection_route
from db.database import createtable,create_users_table

# Create FastAPI app instance
app = FastAPI()


# Include routers
#app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(predection_route, prefix="/prediction", tags=["Prediction"])

# Create the necessary tables in the database
createtable()
create_users_table()

# Define home route
@app.get("/")
def home():
    return {"message": "Welcome to the Multiple Disease Prediction API"}
