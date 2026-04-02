import os
import uuid
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from backend.database.firebase_client import db_client
from backend.workers.orchestrator import handle_firebase_event
from backend.core.scraper import scrape_url
from backend.core.brain import generate_style_contract

load_dotenv() 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI. Attaching DB listener...")
    db_client.listen("/tasks", handle_firebase_event)
    yield
    logger.info("Shutting down FastAPI...")

app = FastAPI(lifespan=lifespan)

class GenerateRequest(BaseModel):
    url: str
    template: str = ""

@app.post("/generate")
async def generate_ad(request: GenerateRequest):
    logger.info(f"Received request to generate ad for {request.url}")
    # 1. Scrape
    scraped_data = await scrape_url(request.url)
    if not scraped_data.get("title"):
        raise HTTPException(status_code=400, detail="Could not scrape URL.")
    
    # 2. Brain generates Style Contract (running sync function in thread)
    style_contract = await asyncio.to_thread(generate_style_contract, scraped_data, request.template)
    
    task_id = str(uuid.uuid4())
    
    # 3. Save to DB
    initial_data = {
        "status": "pending_generation",
        "style_contract": style_contract,
        "input_url": request.url,
        "template": request.template
    }
    db_client.set_data(f"/tasks/{task_id}", initial_data)
    
    # Returns immediately, orchestrator handles generation in background
    return {"task_id": task_id, "status": "pending_generation"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    data = db_client.get_data(f"/tasks/{task_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return data

@app.put("/feedback/{task_id}")
async def submit_feedback(task_id: str, feedback: dict):
    """
    Simulates Gemini Live processing text/voice and updating the contract.
    """
    data = db_client.get_data(f"/tasks/{task_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
        
    contract = data.get("style_contract", {})
    contract.update(feedback)
    
    db_client.update_data(f"/tasks/{task_id}", {
        "style_contract": contract,
        "status": "pending_generation"  # Triggers Orchestrator listener
    })
    
    return {"status": "Updated and re-started generation."}

@app.get("/video/{task_id}")
async def get_video(task_id: str):
    data = db_client.get_data(f"/tasks/{task_id}")
    if not data or not data.get("final_video_url"):
         raise HTTPException(status_code=404, detail="Video not ready or missing")
    
    video_path = data["final_video_url"]
    if os.path.exists(video_path):
        return FileResponse(video_path, media_type="video/mp4")
    raise HTTPException(status_code=404, detail="Video file missing from OS")
