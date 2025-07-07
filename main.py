from fastapi import FastAPI
from app.controllers.approvals_controller import router as approvals_router

app = FastAPI()
app.include_router(approvals_router)