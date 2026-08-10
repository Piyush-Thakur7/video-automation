import os
import time
import json
import random
import threading
from datetime import datetime

STATE_FILE = "config/autopilot_state.json"

class AutoPilotDaemon:
    def __init__(self):
        self.enabled = False
        self.interval_minutes = 60  # Default 1 hour
        self.niches = ["dark_psychology", "facts_curiosities", "tech_ai", "finance_business", "stoicism"]
        self.video_type = "shorts"
        self.privacy_status = "public"
        self.voice_id = "en-US-ChristopherNeural"
        
        self.last_run_time = None
        self.next_run_time = None
        self.total_auto_videos = 0
        self.history = []
        
        self._thread = None
        self._stop_event = threading.Event()
        self._load_state()

    def _save_state(self):
        try:
            os.makedirs("config", exist_ok=True)
            data = {
                "enabled": self.enabled,
                "interval_minutes": self.interval_minutes,
                "niches": self.niches,
                "video_type": self.video_type,
                "privacy_status": self.privacy_status,
                "voice_id": self.voice_id,
                "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
                "next_run_time": self.next_run_time.isoformat() if self.next_run_time else None,
                "total_auto_videos": self.total_auto_videos,
                "history": self.history[-20:]
            }
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[AutoPilot State Save Error] {e}")

    def _load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.enabled = data.get("enabled", False)
                    self.interval_minutes = data.get("interval_minutes", 60)
                    self.niches = data.get("niches", self.niches)
                    self.video_type = data.get("video_type", "shorts")
                    self.privacy_status = data.get("privacy_status", "public")
                    self.voice_id = data.get("voice_id", "en-US-ChristopherNeural")
                    self.total_auto_videos = data.get("total_auto_videos", 0)
                    self.history = data.get("history", [])
                    
                    if data.get("last_run_time"):
                        self.last_run_time = datetime.fromisoformat(data["last_run_time"])
                    if data.get("next_run_time"):
                        self.next_run_time = datetime.fromisoformat(data["next_run_time"])
            except Exception as e:
                print(f"[AutoPilot State Load Error] {e}")

    def get_status(self) -> dict:
        return {
            "enabled": self.enabled,
            "interval_minutes": self.interval_minutes,
            "selected_niches": self.niches,
            "video_type": self.video_type,
            "privacy_status": self.privacy_status,
            "last_run": self.last_run_time.isoformat() if self.last_run_time else None,
            "next_run": self.next_run_time.isoformat() if self.next_run_time and self.enabled else None,
            "total_auto_videos": self.total_auto_videos,
            "history": self.history[-10:]
        }

    def update_config(self, interval_minutes: int = 60, niches: list = None, video_type: str = "shorts", privacy_status: str = "public", voice_id: str = "en-US-ChristopherNeural"):
        self.interval_minutes = max(5, interval_minutes)
        if niches:
            self.niches = niches
        self.video_type = video_type
        self.privacy_status = privacy_status
        self.voice_id = voice_id
        if self.enabled:
            self.next_run_time = datetime.now()
        self._save_state()

    def execute_single_run(self, run_task_fn):
        """Executes a single autonomous video creation and upload task safely."""
        niche = random.choice(self.niches) if self.niches else "facts_curiosities"
        print(f"[AutoPilot Worker] Running autonomous pipeline for niche: {niche}")
        
        start_time = datetime.now()
        try:
            run_info = run_task_fn(
                niche=niche,
                video_type=self.video_type,
                voice_id=self.voice_id,
                privacy_status=self.privacy_status
            )
            
            self.last_run_time = start_time
            self.total_auto_videos += 1
            
            self.history.append({
                "timestamp": self.last_run_time.strftime("%Y-%m-%d %H:%M:%S"),
                "niche": niche,
                "title": run_info.get("title", "Auto Video"),
                "status": "completed",
                "video_url": run_info.get("video_url"),
                "yt_status": run_info.get("yt_status")
            })
        except Exception as e:
            print(f"[AutoPilot Worker Error] {e}")
            self.history.append({
                "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "niche": niche,
                "error": str(e),
                "status": "failed"
            })
        
        self._save_state()

    def start(self, run_task_fn):
        if self.enabled and self._thread and self._thread.is_alive():
            return
        
        self.enabled = True
        self._stop_event.clear()
        if not self.next_run_time or datetime.now() >= self.next_run_time:
            self.next_run_time = datetime.now()
        self._save_state()
        
        def _loop():
            print("[AutoPilot] Daemon scheduler loop started.")
            while not self._stop_event.is_set():
                if self.enabled and self.next_run_time and datetime.now() >= self.next_run_time:
                    print("[AutoPilot] Triggering scheduled autonomous run!")
                    
                    # Schedule next run immediately before launching thread
                    next_sec = self.interval_minutes * 60
                    self.next_run_time = datetime.fromtimestamp(time.time() + next_sec)
                    self._save_state()
                    
                    # Spawn worker thread non-blockingly
                    t = threading.Thread(target=self.execute_single_run, args=(run_task_fn,), daemon=True)
                    t.start()

                time.sleep(5)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.enabled = False
        self._stop_event.set()
        self._save_state()

autopilot_daemon = AutoPilotDaemon()
