import asyncio
import logging
from typing import Any

from backend.database.firebase_client import db_client
from backend.workers.generators import (
    generate_images_mock,
    generate_video_mock,
    generate_music_mock,
    generate_tts_mock,
    generate_text_overlay
)
from backend.synthesizer.engine import synthesize_ad

logger = logging.getLogger(__name__)

async def process_task(task_id: str, data: dict):
    """
    Orchestrates the parallel generation and the final synthesis.
    """
    logger.info(f"Orchestrator: Processing task {task_id}")
    db_client.update_data(f"/tasks/{task_id}", {"status": "generating"})
    
    style_contract = data.get("style_contract", {})
    
    # Extract values from style contract
    prompts = style_contract.get("prompts_for_images", [])
    bpm = style_contract.get("audio_bpm", 120)
    vibe = style_contract.get("audio_vibe", "Electronic")
    narrative = style_contract.get("tts_narration", "Welcome.")
    visual_style = style_contract.get("visual_style", "Cinematic")
    hero_product = style_contract.get("hero_product", "Product")
    punchlines = style_contract.get("ad_punchlines", ["Amazing Brand", "Quality Service", "Check us Out"])


    # Define parallel tasks
    async def video_pipeline():
        images = await generate_images_mock(prompts)
        # We now keep ALL images for the slideshow collage
        best_image = images[0] if images else "tmp/mock_image_0.jpg"
        video_path = await generate_video_mock(best_image, visual_style, hero_product)
        return video_path, images or [best_image]

    # Run pipelines concurrently
    video_task = asyncio.create_task(video_pipeline())
    audio_task = asyncio.create_task(generate_music_mock(bpm, vibe))
    tts_task = asyncio.create_task(generate_tts_mock(narrative))
    
    async def punchline_pipeline():
        overlay_paths = []
        for i, text in enumerate(punchlines):
            path = await generate_text_overlay(text, i)
            overlay_paths.append(path)
        return overlay_paths
    
    punchline_task = asyncio.create_task(punchline_pipeline())

    logger.info("Orchestrator: Waiting for parallel generation to finish...")
    (video_path, image_paths), audio_path, tts_path, overlay_paths = await asyncio.gather(
        video_task, audio_task, tts_task, punchline_task
    )
    logger.info("Orchestrator: All GENERATION complete. Starting Synthesis.")

    db_client.update_data(f"/tasks/{task_id}", {"status": "synthesizing"})

    # Trigger Synthesizer
    try:
        final_video = await synthesize_ad(task_id, video_path, image_paths, audio_path, tts_path, overlay_paths)
        logger.info(f"Orchestrator: Synthesis complete: {final_video}")
        db_client.update_data(f"/tasks/{task_id}", {
            "status": "completed",
            "final_video_url": final_video
        })
    except Exception as e:
        logger.error(f"Orchestrator: Synthesis failed: {e}")
        db_client.update_data(f"/tasks/{task_id}", {"status": "failed", "error": str(e)})


def _run_async_in_thread(coroutine):
    """Helper to run async code inside the callback thread without blocking the loop."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # If loop is already running, create a task
    if loop.is_running():
        asyncio.create_task(coroutine)
    else:
        loop.run_until_complete(coroutine)

def handle_firebase_event(event: Any):
    """
    Callback for database changes. Triggers when /tasks node changes.
    """
    # Note: Event object from firebase-admin looks like:
    # event.path (e.g. '/task_xyz')
    # event.data (e.g. dict with the structure)
    
    # In the mock we pass paths like /task_xyz.
    path = event.path.strip('/')
    data = event.data

    if not data or not isinstance(data, dict):
        return

    # Check if a single task triggered or if it's the root initialization sync
    if "status" in data:
        # Single task update
        task_id = path
        if data["status"] == "pending_generation":
            _run_async_in_thread(process_task(task_id, data))
    else:
        # Multiple tasks might be present (e.g. init event of the root /tasks path)
        for task_id, task_data in data.items():
            if isinstance(task_data, dict) and task_data.get("status") == "pending_generation":
                _run_async_in_thread(process_task(task_id, task_data))
