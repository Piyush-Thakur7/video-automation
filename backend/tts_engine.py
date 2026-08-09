import asyncio
import os
import json
import edge_tts

AVAILABLE_VOICES = [
    {"id": "en-US-ChristopherNeural", "name": "Christopher (Male - Deep & Authoritative)", "gender": "Male", "locale": "en-US"},
    {"id": "en-US-GuyNeural", "name": "Guy (Male - Engaging & Energetic)", "gender": "Male", "locale": "en-US"},
    {"id": "en-US-JennyNeural", "name": "Jenny (Female - Warm & Clear)", "gender": "Female", "locale": "en-US"},
    {"id": "en-US-AvaNeural", "name": "Ava (Female - Expressive & Professional)", "gender": "Female", "locale": "en-US"},
    {"id": "en-GB-RyanNeural", "name": "Ryan (British Male - Sophisticated)", "gender": "Male", "locale": "en-GB"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (British Female - Elegant)", "gender": "Female", "locale": "en-GB"},
    {"id": "en-AU-WilliamNeural", "name": "William (Australian Male - Smooth)", "gender": "Male", "locale": "en-AU"},
]

class TTSEngine:
    def __init__(self, output_dir: str = "storage/audio"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def get_voices(self):
        return AVAILABLE_VOICES

    async def generate_speech_async(self, text: str, voice: str = "en-US-ChristopherNeural", rate: str = "+0%", pitch: str = "+0Hz", output_path: str = None) -> dict:
        if not output_path:
            filename = f"tts_{hash(text + voice + rate)}&.mp3".replace("-", "n")
            output_path = os.path.join(self.output_dir, filename)

        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        
        subtitles = []
        word_timestamps = []

        submaker = edge_tts.SubMaker()

        with open(output_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)
                    word_timestamps.append({
                        "text": chunk["text"],
                        "offset": chunk["offset"] / 10000, # convert 100ns units to ms
                        "duration": chunk["duration"] / 10000
                    })

        srt_content = submaker.get_srt()
        srt_path = output_path.rsplit(".", 1)[0] + ".srt"
        with open(srt_path, "w", encoding="utf-8") as srt_file:
            srt_file.write(srt_content)

        return {
            "audio_path": output_path,
            "srt_path": srt_path,
            "word_timestamps": word_timestamps
        }

    def generate_speech(self, text: str, voice: str = "en-US-ChristopherNeural", rate: str = "+0%", pitch: str = "+0Hz", output_path: str = None) -> dict:
        return asyncio.run(self.generate_speech_async(text, voice, rate, pitch, output_path))

tts_engine = TTSEngine()
