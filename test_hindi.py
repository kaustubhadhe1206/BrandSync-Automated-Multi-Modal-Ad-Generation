import asyncio
from backend.workers.orchestrator import process_task
from backend.database.firebase_client import db_client
import sys

async def main():
    data = {"style_contract": {
        "prompts_for_images": ["A test image"],
        "tts_narration": "यहाँ कुछ हिंदी कथन है।", 
        "audio_bpm": 120,
        "audio_vibe": "Epic",
        "visual_style": "Cinematic",
        "hero_product": "Test",
        "ad_punchlines": ["Test One"]
    }}
    task_id = "test_hindi_task"
    db_client.set_data(f"/tasks/{task_id}", data)
    await process_task(task_id, data)
    print("FINISHED")
    print(db_client.get_data(f"/tasks/{task_id}"))

asyncio.run(main())
