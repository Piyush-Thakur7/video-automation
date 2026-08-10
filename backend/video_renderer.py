import os
import shutil
import subprocess
import uuid
from asset_manager import asset_manager
from script_generator import script_gen
from tts_engine import tts_engine

class VideoRenderer:
    def __init__(self, output_dir: str = "storage/renders", temp_dir: str = "storage/temp", bgm_dir: str = "storage/bgm"):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.bgm_dir = bgm_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.bgm_dir, exist_ok=True)

    def _get_font_path(self) -> str:
        """Cross-platform font file finder for Windows, macOS, and Linux cloud environments (Render)."""
        possible_paths = [
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                return p.replace("\\", "/").replace(":", "\\:")
        return ""

    def render_video(self, job_id: str, script_data: dict, voice_id: str = "en-US-ChristopherNeural", progress_callback=None) -> dict:
        """
        Renders a full 1080p MP4 video with PER-SCENE TTS audio (no repeating voice), synced subtitles, and ambient BGM.
        """
        def update_progress(pct: float, msg: str):
            if progress_callback:
                progress_callback(job_id, pct, msg)

        update_progress(5.0, "Initiating scene rendering pipeline...")

        is_shorts = script_data.get("video_type", "shorts") == "shorts"
        res_w, res_h = (1080, 1920) if is_shorts else (1920, 1080)

        scenes = script_data.get("scenes", [])
        total_scenes = len(scenes)

        scene_clips = []

        for idx, scene in enumerate(scenes, 1):
            pct = 10.0 + (idx / total_scenes) * 60.0
            update_progress(pct, f"Rendering scene {idx}/{total_scenes}: {scene.get('type')}")

            search_term = scene.get("search_term", "abstract cinematic")
            asset_path = asset_manager.fetch_scene_media(search_term=search_term, is_shorts=is_shorts, scene_idx=idx)

            spoken_text = scene.get("text", "")
            
            # Synthesize TTS audio SPECIFICALLY for this scene's text (prevents voice repetition)
            scene_audio_path = os.path.join(self.temp_dir, f"{job_id}_scene_{idx}_tts.mp3")
            audio_info = tts_engine.generate_speech(text=spoken_text, voice=voice_id, output_path=scene_audio_path)
            
            scene_duration = self._get_media_duration(audio_info["audio_path"])
            if scene_duration < 2.0:
                scene_duration = 2.0

            clip_path = self._create_scene_clip(
                job_id=job_id,
                scene_num=idx,
                asset_path=asset_path,
                audio_path=audio_info["audio_path"],
                duration=scene_duration,
                res_w=res_w,
                res_h=res_h,
                spoken_text=spoken_text,
                is_shorts=is_shorts
            )
            scene_clips.append(clip_path)

        update_progress(75.0, "Concatenating scene video clips...")

        # Concat video clips
        concat_list_path = os.path.join(self.temp_dir, f"{job_id}_concat.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for c_file in scene_clips:
                clean_path = os.path.abspath(c_file).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        raw_concat_video = os.path.join(self.temp_dir, f"{job_id}_raw.mp4")

        concat_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            raw_concat_video
        ]
        subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        update_progress(88.0, "Mixing ambient background music & finalizing output...")

        final_output_path = os.path.join(self.output_dir, f"{job_id}_{script_data.get('video_type', 'shorts')}.mp4")

        # Select & Resolve Background Music Track
        bgm_track_name = script_data.get("bg_music", "none")
        if not bgm_track_name:
            bgm_track_name = "none"

        if bgm_track_name.lower() in ["none", "off", "no_bgm", "disabled"]:
            print("[VideoRenderer] Background music set to NONE. Using pure voiceover audio.")
            shutil.copy(raw_concat_video, final_output_path)
        else:
            bgm_path = self._get_or_create_bgm(bgm_track_name)
            # Mix voice audio (input 0) with looping BGM track (input 1)
            mix_cmd = [
                "ffmpeg", "-y",
                "-i", raw_concat_video,
                "-stream_loop", "-1", "-i", bgm_path,
                "-filter_complex", "[1:a]volume=0.35[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                final_output_path
            ]
            try:
                subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"[VideoRenderer] BGM mixing fallback: {e}")
                shutil.copy(raw_concat_video, final_output_path)

        # Clean up temporary clip files after successful render to prevent disk bloat
        try:
            for clip in scene_clips:
                if os.path.exists(clip):
                    os.remove(clip)
            if os.path.exists(raw_concat_video):
                os.remove(raw_concat_video)
            if os.path.exists(concat_list_path):
                os.remove(concat_list_path)
        except Exception as cleanup_err:
            print(f"[VideoRenderer] Cleanup notice: {cleanup_err}")

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
            return 4.0

    def _wrap_text(self, text: str, max_chars: int = 26) -> str:
        words = text.split()
        lines = []
        curr = []
        curr_len = 0
        for w in words:
            if curr_len + len(w) + 1 > max_chars:
                lines.append(" ".join(curr))
                curr = [w]
                curr_len = len(w)
            else:
                curr.append(w)
                curr_len += len(w) + 1
        if curr:
            lines.append(" ".join(curr))
        return "\n".join(lines)

    def _create_scene_clip(self, job_id: str, scene_num: int, asset_path: str, audio_path: str, duration: float, res_w: int, res_h: int, spoken_text: str, is_shorts: bool) -> str:
        out_clip = os.path.join(self.temp_dir, f"{job_id}_clip_{scene_num}.mp4")
        is_video = asset_path.endswith(".mp4")

        # Format spoken script text into clean 2-3 line viral subtitles
        formatted_subtitle = self._wrap_text(spoken_text, max_chars=24 if is_shorts else 40)
        escaped_subtitle = formatted_subtitle.replace(":", "\\:").replace("'", "").replace('"', "")
        font_path = self._get_font_path()
        font_param = f":fontfile='{font_path}'" if font_path else ""
        
        font_size = 46 if is_shorts else 36
        y_pos = "(h-h/3.2)" if is_shorts else "(h-h/4.5)"

        drawtext_filter = f"drawtext=text='{escaped_subtitle}'{font_param}:fontcolor=yellow:fontsize={font_size}:x=(w-text_w)/2:y={y_pos}:box=1:boxcolor=black@0.75:boxborderw=14:line_spacing=10"

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
        if not bgm_name or bgm_name == "auto" or not bgm_name.endswith(".mp3"):
            bgm_name = "tech_ambient.mp3"

        primary_target = os.path.join(self.bgm_dir, bgm_name)
        if os.path.exists(primary_target):
            return primary_target

        temp_target = os.path.join(self.temp_dir, "bgm", bgm_name)
        os.makedirs(os.path.join(self.temp_dir, "bgm"), exist_ok=True)

        if not os.path.exists(temp_target):
            synth_expr = "0.35*sin(2*3.14159*130.81*t)+0.28*sin(2*3.14159*164.81*t)+0.22*sin(2*3.14159*196.00*t)+0.18*sin(2*3.14159*261.63*t)"
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"aevalsrc=exprs='{synth_expr}':s=44100",
                "-t", "120",
                "-c:a", "libmp3lame", "-b:a", "192k",
                temp_target
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return temp_target

video_renderer = VideoRenderer()
