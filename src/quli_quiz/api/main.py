from fastapi import FastAPI

from quli_quiz.api import models, routes
from quli_quiz.api.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quli Quiz API",
    description="API for the Quli Quiz application",
    version="1.0.0",
)

app.include_router(routes.router, tags=["questions", "quizzes"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Quli Quiz API"}


def start():
    """Entry point for the API server."""
    import uvicorn

    uvicorn.run("quli_quiz.api.main:app", host="0.0.0.0", port=8000, reload=True)
