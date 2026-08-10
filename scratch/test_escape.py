import sys, os
sys.path.append("backend")
from video_renderer import video_renderer

print("Testing FFmpeg subtitle escaping...")
raw_text = "Did you know? 100% of human brains react to 50% more signals!"
wrapped = video_renderer._wrap_text(raw_text, max_chars=24)
escaped = wrapped.replace(":", "\\:").replace("%", "\\%").replace("'", "").replace('"', "").replace("\n", "\\n")
print("Wrapped & Escaped:\n", repr(escaped))

# Test clip creation
try:
    clip_path = video_renderer._create_scene_clip(
        job_id="test_sub_escape",
        scene_num=1,
        asset_path="storage/assets/scene_1_shorts_pexels.mp4",
        audio_path="storage/audio/tts_7316490906808402771&.mp3",
        duration=3.0,
        res_w=1080,
        res_h=1920,
        spoken_text=raw_text,
        is_shorts=True
    )
    print("OK Clip rendering with subtitle escaping SUCCEEDED:", clip_path)
    if os.path.exists(clip_path):
        os.remove(clip_path)
except Exception as e:
    print("FAILED Clip rendering:", e)
