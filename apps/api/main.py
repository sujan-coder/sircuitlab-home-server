from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SircuitLab Home Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "project": "SircuitLab Home Server",
        "status": "online"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
