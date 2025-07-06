from fastapi import FastAPI
from app.controllers.approvals_controller import router as approvals_router

app = FastAPI()
app.include_router(approvals_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
