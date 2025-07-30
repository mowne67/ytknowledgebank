from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pipeline import final_pipeline
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import traceback

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
    
    try:
        markdown = final_pipeline(req.url, language='en')
        if markdown is None:
            logger.error("Pipeline returned None - no summary generated")
            raise HTTPException(status_code=500, detail="Failed to generate summary - no content available")
        
        logger.info("Summary generated successfully")
        return {"markdown": markdown}
        
    except Exception as e:
        error_msg = f"Error during summarization: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return a more specific error message
        if "sign in" in str(e).lower() or "authentication" in str(e).lower():
            raise HTTPException(status_code=401, detail="Authentication required - video may be restricted")
        elif "not found" in str(e).lower() or "unavailable" in str(e).lower():
            raise HTTPException(status_code=404, detail="Video not found or unavailable")
        else:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the YouTube Summarization API. Use the /summarize endpoint to summarize videos."}

@app.get("/health")
def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "YouTube Summarization API"}
