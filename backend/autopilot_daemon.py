import os
import time
import random
import threading
from datetime import datetime

class AutoPilotDaemon:
    def __init__(self, app_context=None):
        self.enabled = False
        self.interval_minutes = 60  # Default 1 hour
        self.niches = ["dark_psychology", "facts_curiosities", "tech_ai", "finance_business", "stoicism"]
        self.video_type = "shorts"
        self.privacy_status = "private"
        self.voice_id = "en-US-ChristopherNeural"
        
        self.last_run_time = None
        self.next_run_time = None
        self.total_auto_videos = 0
        self.history = []
        
        self._thread = None
        self._stop_event = threading.Event()

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
            "history": self.history[-10:]  # Last 10 auto runs
        }

    def update_config(self, interval_minutes: int = 60, niches: list = None, video_type: str = "shorts", privacy_status: str = "private", voice_id: str = "en-US-ChristopherNeural"):
        self.interval_minutes = max(5, interval_minutes)
        if niches:
            self.niches = niches
        self.video_type = video_type
        self.privacy_status = privacy_status
        self.voice_id = voice_id
        if self.enabled:
            self.next_run_time = datetime.now()

    def start(self, run_task_fn):
        if self.enabled:
            return
        self.enabled = True
        self._stop_event.clear()
        self.next_run_time = datetime.now()
        
        def _loop():
            print("[AutoPilot] Daemon started. Checking schedule every 10 seconds...")
            while not self._stop_event.is_set():
                if self.enabled and self.next_run_time and datetime.now() >= self.next_run_time:
                    try:
                        print("[AutoPilot] Triggering scheduled autonomous video generation & upload!")
                        niche = random.choice(self.niches)
                        
                        run_info = run_task_fn(
                            niche=niche,
                            video_type=self.video_type,
                            voice_id=self.voice_id,
                            privacy_status=self.privacy_status
                        )
                        
                        self.last_run_time = datetime.now()
                        self.total_auto_videos += 1
                        
                        self.history.append({
                            "timestamp": self.last_run_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "niche": niche,
                            "title": run_info.get("title", "Auto Video"),
                            "status": run_info.get("status", "completed"),
                            "video_url": run_info.get("video_url"),
                            "yt_status": run_info.get("yt_status")
                        })
                    except Exception as e:
                        print(f"[AutoPilot Error] {e}")
                        self.history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "error": str(e),
                            "status": "failed"
                        })
                    
                    # Schedule next run
                    next_sec = self.interval_minutes * 60
                    self.next_run_time = datetime.fromtimestamp(time.time() + next_sec)
                    print(f"[AutoPilot] Next scheduled run at: {self.next_run_time.strftime('%H:%M:%S')}")
                
                time.sleep(10)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.enabled = False
        self._stop_event.set()

autopilot_daemon = AutoPilotDaemon()
