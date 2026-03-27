from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Intelligent ITSM API"
)

app.include_router(router)