from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pipeline import final_pipeline
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

app = FastAPI()

# Configure loguru
logger.add("logs/ytknowledgebank.log", rotation="1 MB", retention="7 days", level="INFO")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class YouTubeRequest(BaseModel):
    url: str

@app.post("/summarize")
def summarize(req: YouTubeRequest):
    logger.info(f"Received request to summarize URL: {req.url}")
    markdown = final_pipeline(req.url, language='en')
    logger.info("Summary generated successfully")
    return {"markdown": markdown}

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the YouTube Summarization API. Use the /summarize endpoint to summarize videos."}
