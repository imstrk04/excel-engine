from fastapi import FastAPI
from . import routes

app = FastAPI(
    title="Petavue Excel AI Engine",
    description="Developed by Sadakopa Ramakrishnan",
)   

app.include_router(routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Excel AI Engine!"}