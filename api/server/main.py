import uvicorn
from core.config import ALLOW_ORIGINS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.middleware.timeout import TimeoutMiddleware
from server.routes.router import router

app = FastAPI(docs_url="/docs", redoc_url=None)
app.include_router(router)
app.add_middleware(TimeoutMiddleware, timeout=3600)

sub_app = FastAPI(
    title="Paper Chat Recommender API",
    description="",
    version="1.0.0",
)
app.mount("/sub", sub_app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def start():
    uvicorn.run("server.main:app", host="0.0.0.0", port=80, reload=True)
