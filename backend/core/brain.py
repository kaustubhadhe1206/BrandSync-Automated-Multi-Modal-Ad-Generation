import os
import json
import logging
from typing import Dict, Any, List
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Try to load API key (though SDK handles automatically if set in env)
# client = genai.Client()

class Character(BaseModel):
    description: str = Field(description="Visual description of a character or product to feature in the ad.")

class Scene(BaseModel):
    description: str = Field(description="Description of the scene layout and vibe.")

class StyleContract(BaseModel):
    brand_name: str = Field(description="Extracted name of the brand.")
    hero_product: str = Field(description="The primary product/service being advertised (e.g., 'Pizza', 'Sleek Laptop', 'Healthy Salad').")
    core_message: str = Field(description="The main message or value proposition of the ad.")
    visual_style: str = Field(description="The artistic visual style (e.g., 'Cinematic, neon-lit, 4k', 'Minimalist pastel', etc.)")
    prompts_for_images: List[str] = Field(description="3 distinct prompts to generate candidate hero images for the video. MUST focus on the hero_product.", max_length=3, min_length=3)
    audio_bpm: int = Field(description="Suggested BPM (Beats Per Minute) for the soundtrack (e.g., 90 for calm, 120 for upbeat).")
    audio_vibe: str = Field(description="A prompt describing the musical soundtrack vibe for the generation model.")
    tts_narration: str = Field(description="The script for the voice-over narration. MUST be exactly 35 words to fit a 20s ad.")
    ad_punchlines: List[str] = Field(description="3 short, punchy marketing phrases (exactly 2-3 words each) to be overlayed as text during the video.", max_length=3, min_length=3)

def generate_style_contract(scraped_data: Dict[str, str], user_template: str = "") -> dict:
    """
    Invokes Gemini 3 Flash (using gemini-2.5-flash or available model) to generate a structured JSON contract.
    """
    logger.info("Generating Style Contract with Gemini...")
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment.")
            
        client = genai.Client(api_key=api_key)
        # Define model. Assuming 'gemini-2.5-flash' is the available standard flash model
        # Adjust to 3.0 if available, but 2.5 is typical
        model_name = "gemini-2.5-flash"

        prompt = f"""
        You are the central Brain for an automated Video Ad Generator (BrandSync).
        Your task is to analyze the scraped content of a business website and an optional user template, 
        and output a comprehensive 'Style Contract'. This contract will orchestrate downstream generative models 
        for Images (Nano Banana), Video (Veo), Music (Lyria), and TTS naration.

        CRITICAL INSTRUCTIONS:
        1. IDENTIFY THE HERO PRODUCT: Look through the scraped text and identify the core product or service being sold. 
           (e.g., If the website is a pizza place, the hero_product is 'Pizza'. DO NOT suggest 'Sandwiches' or 'Pasta' unless it's a generic food site). 
        2. VISUAL ACCURACY & BRANDING: All 3 'prompts_for_images' MUST feature this 'hero_product'. 
           - One image prompt MUST be a clean 'Hero shot' that includes 'Integrated professional [Brand Name] logo and minimalist typography'.
        3. DYNAMIC TEXT: Create 3 'ad_punchlines' that capture the brand's core value proposition in exactly 2-3 words each.
        4. PRODUCTION TIMINGS: We are building a **20-second Video Ad**. The 'tts_narration' MUST be exactly 35 words long. NO MORE.
        
        Input Website Data:
        URL: {scraped_data.get('url')}
        Title: {scraped_data.get('title')}
        Description: {scraped_data.get('description')}
        Content Snippet: {scraped_data.get('content')[:1500]}

        User Template Preference: {user_template if user_template else 'None (Infer from brand content)'}
        """

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StyleContract,
                temperature=0.7,
            ),
        )
        
        # Parse the JSON response
        contract_json = json.loads(response.text)
        return contract_json

    except Exception as e:
        logger.error(f"Failed to generate Style Contract: {e}")
        # Return fallback mock JSON if API fails
        return {
            "brand_name": "Fallback Brand",
            "hero_product": "Gadjets",
            "core_message": "Discover our amazing products.",
            "visual_style": "Clean, modern, highly detailed, 4k.",
            "prompts_for_images": [
                "A clean, modern product display on a marble table, highly detailed, 4k.",
                "Lifestyle shot of a modern product in a bright living room, realistic.",
                "Abstract sleek representation of modern business, 3d render, blender."
            ],
            "audio_bpm": 110,
            "audio_vibe": "Upbeat, modern corporate electronic music.",
            "tts_narration": "Experience the future of innovation with our quality products. From sleek engineering to limitless potential, we redefine what is possible every single day. See why we are the top standard in our global industry.",
            "ad_punchlines": ["Innovation First", "Sleek Engineering", "Limitless Potential"]
        }
