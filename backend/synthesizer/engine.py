import logging
import asyncio
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, ImageClip, CompositeVideoClip, concatenate_videoclips
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

async def synthesize_ad(task_id: str, video_path: str, image_paths: List[str], audio_path: str, tts_path: str, overlay_paths: List[str]) -> str:
    """
    Cinematic Collage Ad (20s): 8s Motion -> 8s Slideshow (2 images) -> 4s Hero Closer.
    """
    logger.info(f"Synthesizer: Starting 20s Cinematic Collage for {task_id}...")
    output_path = f"tmp/final_synthetic_ad_{task_id}.mp4"

    def merge_media():
        try:
            # 1. Load Primary Components
            motion_clip = VideoFileClip(video_path).resized(width=1280).with_duration(8)
            bgm = AudioFileClip(audio_path)
            tts = AudioFileClip(tts_path)

            # 2. Image Selection (image_paths[0] is typically the Hero/Logo closer)
            hero_path = image_paths[0] if len(image_paths) > 0 else "tmp/mock_image_0.jpg"
            img2_path = image_paths[1] if len(image_paths) > 1 else hero_path
            img3_path = image_paths[2] if len(image_paths) > 2 else hero_path

            # 3. Sequence Assembly
            # Section 1: Motion (0-8s)
            section1 = motion_clip.with_start(0)
            
            # Section 2: Slideshow Build (8-16s)
            slide1 = ImageClip(img2_path, duration=4).resized(width=1280).with_start(8)
            slide2 = ImageClip(img3_path, duration=4).resized(width=1280).with_start(12)
            
            # Section 3: Branded Hero Closer (16-20s)
            closer = ImageClip(hero_path, duration=4).resized(width=1280).with_start(16)
            
            # 4. Dynamic Text Overlays
            text_layers = []
            # Timings: 1-4s (Video), 5-8s (Video), 9-14s (Slideshow)
            timings = [(1, 4), (5, 8), (9, 14)] 
            for i, path in enumerate(overlay_paths[:3]):
                start, end = timings[i]
                txt = ImageClip(path).with_start(start).with_duration(end - start).with_position("center")
                text_layers.append(txt)

            # 5. Composite Final Clip
            final_video_clip = CompositeVideoClip(
                [section1, slide1, slide2, closer] + text_layers,
                size=(1280, 720)
            ).with_duration(20)

            # 6. Audio Mixing
            bgm = bgm.with_volume_scaled(0.15)
            tts = tts.with_start(1.0)
            final_audio = CompositeAudioClip([bgm, tts])
            
            if final_audio.duration > 20:
                final_audio = final_audio.subclipped(0, 20)
            
            # 7. Final Export
            final_video = final_video_clip.with_audio(final_audio)
            final_video.write_videofile(
                output_path, 
                codec='libx264', 
                audio_codec='aac', 
                logger=None,
                fps=24
            )
            
            # Cleanup
            motion_clip.close()
            slide1.close()
            slide2.close()
            closer.close()
            bgm.close()
            tts.close()
            for tx in text_layers: tx.close()
            
            return output_path
        except Exception as e:
            logger.error(f"Synthesizer Engine Error: {e}")
            raise e

    await asyncio.to_thread(merge_media)
    logger.info(f"Synthesizer Result: {output_path}")

    return output_path