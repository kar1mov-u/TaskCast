from fastapi import FastAPI
from .database import create_db_and_tables
from .routes import auth,users,projects,tasks



app=FastAPI()

@app.on_event("startup")
def  on_startup():
    create_db_and_tables()

app.include_router(auth.router)
app.include_router(users.router)



