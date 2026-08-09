import os
import json
import uuid
import asyncio
import threading
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from script_generator import script_gen, NICHE_TEMPLATES
from tts_engine import tts_engine
from asset_manager import asset_manager
from video_renderer import video_renderer
from youtube_publisher import youtube_publisher
from autopilot_daemon import autopilot_daemon

app = FastAPI(title="AutoTube AI Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("storage", exist_ok=True)
os.makedirs("config", exist_ok=True)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

RENDER_JOBS = {}

class ScriptRequest(BaseModel):
    niche: str = Field(default="dark_psychology")
    topic: str = Field(default="")
    video_type: str = Field(default="shorts")
    tone: str = Field(default="dramatic")

class RenderRequest(BaseModel):
    script_data: dict
    voice_id: str = "en-US-ChristopherNeural"
    bgm_track: str = "dark_suspense.mp3"
    bgm_volume: float = 0.25

class YouTubeUploadRequest(BaseModel):
    video_path: str
    title: str
    description: str
    tags: list
    privacy_status: str = "private"

class AutoPilotConfigRequest(BaseModel):
    interval_minutes: int = 60
    niches: list = ["dark_psychology", "tech_ai", "facts_curiosities"]
    video_type: str = "shorts"
    privacy_status: str = "private"
    voice_id: str = "en-US-ChristopherNeural"

@app.get("/")
def root_status():
    return {
        "name": "AutoTube AI Automation Engine",
        "status": "online",
        "docs": "http://127.0.0.1:8000/docs",
        "frontend_studio": "http://127.0.0.1:5173",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "system": "AutoTube AI",
        "version": "1.0.0",
        "ffmpeg": True,
        "edge_tts": True,
        "autopilot_enabled": autopilot_daemon.enabled
    }

@app.get("/api/niches")
def get_niches():
    return {
        "niches": [
            {
                "key": k,
                "name": v["name"],
                "bg_music": v["bg_music"],
                "sample_topics": v["sample_topics"],
                "keywords": v["visual_keywords"]
            }
            for k, v in NICHE_TEMPLATES.items()
        ]
    }

@app.post("/api/script/generate")
def generate_script(req: ScriptRequest):
    try:
        res = script_gen.generate_script(
            niche=req.niche,
            topic=req.topic,
            video_type=req.video_type,
            tone=req.tone
        )
        return {"success": True, "script": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/voices")
def get_voices():
    return {"voices": tts_engine.get_voices()}

@app.post("/api/tts/preview")
def preview_voice(voice_id: str = "en-US-ChristopherNeural", text: str = "Welcome to AutoTube AI studio. Voice synthesis test."):
    try:
        out = tts_engine.generate_speech(text=text, voice=voice_id)
        rel_path = "/" + out["audio_path"].replace("\\", "/")
        return {"success": True, "audio_url": rel_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/render")
def start_video_render(req: RenderRequest):
    job_id = f"job_{uuid.uuid4().hex[:8]}"

    # Inject chosen BGM track into script_data if specified
    if req.bgm_track and req.bgm_track != "auto":
        req.script_data["bg_music"] = req.bgm_track
    else:
        req.script_data["bg_music"] = script_gen.auto_select_bgm(req.script_data.get("topic", ""), req.script_data.get("niche", ""))

    RENDER_JOBS[job_id] = {
        "job_id": job_id,
        "progress": 0.0,
        "status": "queued",
        "message": "Job queued for rendering...",
        "output": None,
        "error": None
    }

    def update_job(j_id, progress, msg):
        if j_id in RENDER_JOBS:
            RENDER_JOBS[j_id]["progress"] = progress
            RENDER_JOBS[j_id]["message"] = msg
            if progress >= 100.0:
                RENDER_JOBS[j_id]["status"] = "completed"
            else:
                RENDER_JOBS[j_id]["status"] = "rendering"

    def run_render_task():
        try:
            res = video_renderer.render_video(
                job_id=job_id,
                script_data=req.script_data,
                voice_id=req.voice_id,
                progress_callback=update_job
            )
            rel_path = "/" + res["output_path"].replace("\\", "/")
            res["video_url"] = rel_path
            RENDER_JOBS[job_id]["output"] = res
            RENDER_JOBS[job_id]["status"] = "completed"
        except Exception as err:
            RENDER_JOBS[job_id]["status"] = "failed"
            RENDER_JOBS[job_id]["error"] = str(err)
            print(f"[RenderError] {err}")

    threading.Thread(target=run_render_task, daemon=True).start()

    return {"success": True, "job_id": job_id, "status": "queued"}

@app.get("/api/video/status/{job_id}")
def get_render_status(job_id: str):
    if job_id not in RENDER_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return RENDER_JOBS[job_id]

@app.get("/api/video/library")
def get_video_library():
    renders_dir = "storage/renders"
    if not os.path.exists(renders_dir):
        return {"videos": []}

    videos = []
    for file in os.listdir(renders_dir):
        if file.endswith(".mp4"):
            f_path = os.path.join(renders_dir, file)
            size_mb = round(os.path.getsize(f_path) / (1024 * 1024), 2)
            rel_url = "/" + f_path.replace("\\", "/")
            is_shorts = "shorts" in file
            videos.append({
                "filename": file,
                "path": f_path,
                "url": rel_url,
                "size_mb": size_mb,
                "created_at": os.path.getmtime(f_path),
                "is_shorts": is_shorts
            })
    
    videos.sort(key=lambda x: x["created_at"], reverse=True)
    return {"videos": videos}

@app.get("/api/youtube/status")
def get_youtube_status():
    return youtube_publisher.get_channel_info()

@app.get("/api/youtube/auth-url")
def get_youtube_auth_url():
    auth_url = youtube_publisher.get_auth_url()
    if not auth_url:
        raise HTTPException(status_code=400, detail="client_secrets.json is missing in config/")
    return {"auth_url": auth_url}

@app.get("/api/youtube/callback", response_class=HTMLResponse)
def youtube_auth_callback(code: str):
    success = youtube_publisher.exchange_code(code)
    if success:
        info = youtube_publisher.get_channel_info()
        ch_title = info.get("channel", {}).get("title", "Your Channel")
        return f"""
        <html>
            <body style="font-family: sans-serif; background: #0f172a; color: #fff; text-align: center; padding-top: 50px;">
                <h1 style="color: #34d399;">✓ YouTube Channel Connected!</h1>
                <h2>Connected to: {ch_title}</h2>
                <p>Your OAuth token has been saved to config/youtube_token.json.</p>
                <p>You can close this tab and return to AutoTube AI Studio!</p>
            </body>
        </html>
        """
    else:
        return """
        <html>
            <body style="font-family: sans-serif; background: #0f172a; color: #fff; text-align: center; padding-top: 50px;">
                <h1 style="color: #ff0055;">OAuth Error</h1>
                <p>Failed to exchange authorization code for access token.</p>
            </body>
        </html>
        """

class SyncCredentialsRequest(BaseModel):
    client_secrets_json: str = None
    youtube_token_json: str = None

@app.post("/api/sync/credentials")
def sync_credentials_to_cloud(req: SyncCredentialsRequest):
    os.makedirs("config", exist_ok=True)
    if req.client_secrets_json:
        with open("config/client_secrets.json", "w", encoding="utf-8") as f:
            f.write(req.client_secrets_json)
    if req.youtube_token_json:
        with open("config/youtube_token.json", "w", encoding="utf-8") as f:
            f.write(req.youtube_token_json)
    return {"success": True, "message": "Credentials successfully synced to Cloud Engine!"}

@app.post("/api/youtube/credentials")
def save_youtube_credentials(client_secrets_json: str):
    try:
        data = json.loads(client_secrets_json)
        with open("config/client_secrets.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return {"success": True, "message": "Client secrets saved to config/client_secrets.json"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

@app.post("/api/youtube/upload")
def upload_to_youtube(req: YouTubeUploadRequest):
    res = youtube_publisher.upload_video(
        video_path=req.video_path,
        title=req.title,
        description=req.description,
        tags=req.tags,
        privacy_status=req.privacy_status
    )
    return res

# --- AUTOPILOT DAEMON ENDPOINTS ---

def _run_autonomous_job(niche: str, video_type: str, voice_id: str, privacy_status: str) -> dict:
    job_id = f"auto_{uuid.uuid4().hex[:8]}"
    print(f"[AutoPilot Task] Generating script for niche: {niche}")
    script_data = script_gen.generate_script(niche=niche, topic="", video_type=video_type)
    
    print(f"[AutoPilot Task] Rendering video {job_id}...")
    res = video_renderer.render_video(
        job_id=job_id,
        script_data=script_data,
        voice_id=voice_id
    )
    rel_url = "/" + res["output_path"].replace("\\", "/")
    
    # Upload to YouTube if authenticated
    yt_res = youtube_publisher.upload_video(
        video_path=res["output_path"],
        title=script_data["title"],
        description=script_data["seo"]["description"],
        tags=script_data["seo"]["tags"],
        privacy_status=privacy_status
    )

    return {
        "title": script_data["title"],
        "status": "completed",
        "video_url": rel_url,
        "yt_status": yt_res.get("video_url") if yt_res.get("success") else "Saved to local library (YT credentials pending)"
    }

@app.get("/api/autopilot/status")
def get_autopilot_status():
    return autopilot_daemon.get_status()

@app.post("/api/autopilot/toggle")
def toggle_autopilot(enable: bool = True):
    if enable:
        autopilot_daemon.start(_run_autonomous_job)
    else:
        autopilot_daemon.stop()
    return {"success": True, "enabled": autopilot_daemon.enabled}

@app.post("/api/autopilot/config")
def set_autopilot_config(req: AutoPilotConfigRequest):
    autopilot_daemon.update_config(
        interval_minutes=req.interval_minutes,
        niches=req.niches,
        video_type=req.video_type,
        privacy_status=req.privacy_status,
        voice_id=req.voice_id
    )
    return {"success": True, "status": autopilot_daemon.get_status()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
