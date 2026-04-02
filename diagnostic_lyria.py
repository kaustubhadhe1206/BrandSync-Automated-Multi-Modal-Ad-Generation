import os
import asyncio
import logging
from google import genai
from dotenv import load_dotenv

load_dotenv()

async def test_lyria():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("lyria_test")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return
        
    client = genai.Client(api_key=api_key)
    prompt = "INSTRUMENTAL ONLY, happy corporate music, 120 BPM"
    
    print(f"Calling Lyria 3 with prompt: {prompt}")
    try:
        response = client.models.generate_content(
            model='lyria-3-pro-preview',
            contents=prompt
        )
        print("Response received.")
        print(f"Candidates: {len(response.candidates)}")
        for i, candidate in enumerate(response.candidates):
             print(f"Candidate {i} finish reason: {candidate.finish_reason}")
             if candidate.content and candidate.content.parts:
                 for j, part in enumerate(candidate.content.parts):
                     print(f"Part {j} type: {type(part)}")
                     if hasattr(part, 'inline_data'):
                         print(f"Part {j} has inline_data.")
                     if hasattr(part, 'text'):
                         print(f"Part {j} text: {part.text[:100]}")
    except Exception as e:
        print(f"Lyria 3 Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_lyria())
