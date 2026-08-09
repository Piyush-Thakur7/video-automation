import os
import time
import json
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont

class VideoRenderer:
    def __init__(self, output_dir: str = "storage/renders", temp_dir: str = "storage/temp"):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)

    def render_video(self, job_id: str, script_data: dict, voice_id: str, tts_engine, asset_manager, progress_callback=None) -> dict:
        """
        Renders complete video (Shorts 9:16 or Longform 16:9) with TTS audio, stock visuals, dynamic subtitles, and BGM.
        """
        def update_progress(percent: float, message: str):
            print(f"[{job_id}] [{percent}%] {message}")
            if progress_callback:
                progress_callback(job_id, percent, message)

        update_progress(5.0, "Synthesizing voiceover and generating timestamps...")

        is_shorts = script_data.get("video_type") == "shorts"
        res_w, res_h = (1080, 1920) if is_shorts else (1920, 1080)

        scenes = script_data.get("scenes", [])
        scene_files = []
        concat_list_path = os.path.join(self.temp_dir, f"{job_id}_concat.txt")

        total_scenes = len(scenes)
        scene_audio_paths = []

        for idx, scene in enumerate(scenes):
            scene_num = idx + 1
            scene_pct = 10.0 + (idx / total_scenes) * 45.0
            update_progress(round(scene_pct, 1), f"Processing scene {scene_num}/{total_scenes}: {scene['type']}")

            # Generate TTS audio for this scene
            tts_res = tts_engine.generate_speech(
                text=scene["text"],
                voice=voice_id,
                output_path=os.path.join(self.temp_dir, f"{job_id}_scene_{scene_num}.mp3")
            )
            audio_path = tts_res["audio_path"]
            scene_audio_paths.append(audio_path)

            audio_duration = self._get_media_duration(audio_path)

            # Fetch visual asset (video or image)
            search_term = scene.get("search_term", "abstract cinematic")
            asset_path = asset_manager.fetch_scene_media(search_term, is_shorts=is_shorts, scene_idx=scene_num)

            # Create dynamic scene clip (standardized duration, motion zoom, subtitles)
            scene_video = self._create_scene_clip(
                job_id=job_id,
                scene_num=scene_num,
                asset_path=asset_path,
                audio_path=audio_path,
                duration=audio_duration,
                res_w=res_w,
                res_h=res_h,
                overlay_text=scene.get("overlay_text", ""),
                is_shorts=is_shorts
            )
            scene_files.append(scene_video)

        update_progress(60.0, "Concatenating scene clips...")
        
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for s_file in scene_files:
                abs_path = os.path.abspath(s_file).replace("\\", "/")
                f.write(f"file '{abs_path}'\n")

        raw_concat_video = os.path.join(self.temp_dir, f"{job_id}_raw_concat.mp4")

        # FFmpeg concat command
        concat_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            raw_concat_video
        ]
        subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        update_progress(80.0, "Mixing ambient background music & finalizing output...")

        final_output_path = os.path.join(self.output_dir, f"{job_id}_{script_data.get('video_type', 'shorts')}.mp4")

        # Mix background music
        bgm_path = self._get_or_create_bgm(script_data.get("bg_music", "tech_ambient.mp3"))

        mix_cmd = [
            "ffmpeg", "-y",
            "-i", raw_concat_video,
            "-stream_loop", "-1", "-i", bgm_path,
            "-filter_complex", "[1:a]volume=0.25[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            final_output_path
        ]
        
        try:
            subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            shutil.copy(raw_concat_video, final_output_path)

        update_progress(100.0, "Video rendering complete!")

        return {
            "job_id": job_id,
            "output_path": final_output_path,
            "file_size_mb": round(os.path.getsize(final_output_path) / (1024 * 1024), 2),
            "video_type": script_data.get("video_type"),
            "resolution": f"{res_w}x{res_h}"
        }

    def _get_media_duration(self, file_path: str) -> float:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            return float(res.stdout.strip())
        except Exception:
            return 5.0

    def _create_scene_clip(self, job_id: str, scene_num: int, asset_path: str, audio_path: str, duration: float, res_w: int, res_h: int, overlay_text: str, is_shorts: bool) -> str:
        out_clip = os.path.join(self.temp_dir, f"{job_id}_clip_{scene_num}.mp4")
        is_video = asset_path.endswith(".mp4")

        escaped_overlay = overlay_text.replace(":", "\\:").replace("'", "").replace('"', "")
        font_path = "C\\:/Windows/Fonts/arialbd.ttf"
        
        font_size = 48 if is_shorts else 38
        y_pos = "(h-h/4)" if is_shorts else "(h-h/6)"

        drawtext_filter = f"drawtext=fontfile='{font_path}':text='{escaped_overlay}':fontcolor=yellow:fontsize={font_size}:x=(w-text_w)/2:y={y_pos}:box=1:boxcolor=black@0.7:boxborderw=12"

        if is_video:
            filter_str = f"[0:v]scale={res_w}:{res_h}:force_original_aspect_ratio=increase,crop={res_w}:{res_h},{drawtext_filter}[v]"
            cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "-1", "-i", asset_path,
                "-i", audio_path,
                "-filter_complex", filter_str,
                "-map", "[v]", "-map", "1:a",
                "-t", str(duration),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac",
                out_clip
            ]
        else:
            # Ken Burns camera zoom/pan motion for dynamic moving video
            filter_str = f"[0:v]scale={res_w*2}:{res_h*2}:force_original_aspect_ratio=increase,crop={res_w*2}:{res_h*2},zoompan=z='min(zoom+0.0015,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:fps=30:s={res_w}x{res_h},{drawtext_filter}[v]"
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", asset_path,
                "-i", audio_path,
                "-filter_complex", filter_str,
                "-map", "[v]", "-map", "1:a",
                "-t", str(duration),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac",
                out_clip
            ]

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_clip

    def _get_or_create_bgm(self, bgm_name: str) -> str:
        bgm_dir = os.path.join(self.temp_dir, "bgm")
        os.makedirs(bgm_dir, exist_ok=True)
        target = os.path.join(bgm_dir, bgm_name)

        if not os.path.exists(target):
            # Generate synth audio track if specific track missing
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "aevalsrc=exprs='0.1*sin(2*PI*110*t)+0.08*sin(2*PI*164.8*t)':s=44100",
                "-t", "60",
                "-c:a", "libmp3lame", "-b:a", "192k",
                target
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return target

video_renderer = VideoRenderer()
