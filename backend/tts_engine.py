import asyncio
import os
import json
import time
import edge_tts
from gtts import gTTS
import pyttsx3

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

        # Retry loop for Edge-TTS (up to 3 attempts with exponential backoff)
        last_err = None
        for attempt in range(1, 4):
            try:
                communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
                submaker = edge_tts.SubMaker()
                word_timestamps = []

                with open(output_path, "wb") as file:
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            file.write(chunk["data"])
                        elif chunk["type"] == "WordBoundary":
                            submaker.feed(chunk)
                            word_timestamps.append({
                                "text": chunk["text"],
                                "offset": chunk["offset"] / 10000,
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
            except Exception as err:
                last_err = err
                print(f"[TTSEngine Edge-TTS Retry {attempt}/3] {err}")
                await asyncio.sleep( attempt * 1.5 )

        # Fallback 1: gTTS (Google Text-To-Speech)
        print(f"[TTSEngine] Falling back to gTTS (Google Cloud TTS) due to: {last_err}")
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            srt_path = output_path.rsplit(".", 1)[0] + ".srt"
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(f"1\n00:00:00,000 --> 00:00:05,000\n{text}\n")
            return {
                "audio_path": output_path,
                "srt_path": srt_path,
                "word_timestamps": []
            }
        except Exception as gtts_err:
            print(f"[TTSEngine gTTS Fallback Error] {gtts_err}")

        # Fallback 2: Offline pyttsx3 voice engine
        print("[TTSEngine] Falling back to pyttsx3 offline speech synthesizer.")
        engine = pyttsx3.init()
        wav_path = output_path.rsplit(".", 1)[0] + ".wav"
        engine.save_to_file(text, wav_path)
        engine.runAndWait()

        # Convert WAV to MP3 via FFmpeg
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-c:a", "libmp3lame", "-b:a", "192k", output_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(wav_path):
            os.remove(wav_path)

        srt_path = output_path.rsplit(".", 1)[0] + ".srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(f"1\n00:00:00,000 --> 00:00:05,000\n{text}\n")

        return {
            "audio_path": output_path,
            "srt_path": srt_path,
            "word_timestamps": []
        }

    def generate_speech(self, text: str, voice: str = "en-US-ChristopherNeural", rate: str = "+0%", pitch: str = "+0Hz", output_path: str = None) -> dict:
        return asyncio.run(self.generate_speech_async(text, voice, rate, pitch, output_path))

tts_engine = TTSEngine()
