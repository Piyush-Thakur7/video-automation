import os
import shutil
import subprocess
import time
import re

class VideoRenderer:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = storage_dir
        self.assets_dir = os.path.join(storage_dir, "assets")
        self.temp_dir = os.path.join(storage_dir, "temp")
        self.output_dir = os.path.join(storage_dir, "renders")
        self.bgm_dir = os.path.join(storage_dir, "bgm")

        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.bgm_dir, exist_ok=True)

    def _get_font_path(self) -> str:
        possible_paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/impact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                return p.replace("\\", "/").replace(":", "\\:")
        return ""

    def _chunk_text_to_phrases(self, text: str, max_words: int = 3, max_chars: int = 18) -> list:
        """Splits full scene text into short, punchy 2-4 word phrases for TikTok/Shorts viral timing."""
        words = text.split()
        if not words:
            return [""]
        
        phrases = []
        curr = []
        curr_len = 0
        for w in words:
            if len(curr) >= max_words or (curr_len + len(w) + 1 > max_chars and curr):
                phrases.append(" ".join(curr))
                curr = [w]
                curr_len = len(w)
            else:
                curr.append(w)
                curr_len += len(w) + 1
        if curr:
            phrases.append(" ".join(curr))
        return phrases

    def render_video(self, job_id: str, script_data: dict, voice_id: str = "en-US-ChristopherNeural", progress_callback=None) -> dict:
        from tts_engine import tts_engine
        from asset_manager import asset_manager

        def update_progress(pct: float, msg: str):
            if progress_callback:
                progress_callback(pct, msg)
            print(f"[{job_id}] Progress: {pct}% - {msg}")

        update_progress(5.0, "Starting video rendering pipeline...")

        is_shorts = script_data.get("video_type", "shorts") == "shorts"
        res_w = 1080 if is_shorts else 1920
        res_h = 1920 if is_shorts else 1080
        aspect = "portrait" if is_shorts else "landscape"

        scenes = script_data.get("scenes", [])
        scene_clips = []
        scene_durations = []

        total_scenes = len(scenes)

        for idx, scene in enumerate(scenes):
            scene_num = scene.get("scene_num", idx + 1)
            text = scene.get("text", "")
            search_term = scene.get("search_term", "abstract cinematic")

            pct = 10.0 + (idx / total_scenes) * 60.0
            update_progress(pct, f"Rendering scene {scene_num}/{total_scenes}: {scene.get('type', 'Beat')}")

            # 1. Generate Voiceover TTS for Scene
            audio_filename = f"{job_id}_scene_{scene_num}_tts.mp3"
            audio_path = os.path.join(self.temp_dir, audio_filename)
            tts_engine.generate_speech(text, voice_id, output_path=audio_path)

            audio_duration = self._get_media_duration(audio_path)
            # Add small padding for natural pacing
            clip_duration = max(2.5, audio_duration + 0.3)
            scene_durations.append(clip_duration)

            # 2. Fetch Pexels/Stock B-Roll Media Asset
            asset_path = asset_manager.fetch_scene_media(
                search_term=search_term,
                is_shorts=is_shorts,
                scene_idx=scene_num
            )

            # 3. Create Scene Clip with Dynamic Timed Phrase Subtitles & Motion
            clip_path = self._create_scene_clip(
                job_id=job_id,
                scene_num=scene_num,
                asset_path=asset_path,
                audio_path=audio_path,
                duration=clip_duration,
                res_w=res_w,
                res_h=res_h,
                spoken_text=text,
                is_shorts=is_shorts
            )
            scene_clips.append(clip_path)

        update_progress(75.0, "Concatenating scenes with professional transitions...")

        raw_concat_video = os.path.join(self.temp_dir, f"{job_id}_raw.mp4")
        self._concatenate_clips_with_transitions(scene_clips, scene_durations, raw_concat_video, res_w, res_h)

        update_progress(88.0, "Mixing background music & finalizing video...")

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

        # Cleanup temporary files
        try:
            for clip in scene_clips:
                if os.path.exists(clip):
                    os.remove(clip)
            if os.path.exists(raw_concat_video):
                os.remove(raw_concat_video)
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

    def _create_scene_clip(self, job_id: str, scene_num: int, asset_path: str, audio_path: str, duration: float, res_w: int, res_h: int, spoken_text: str, is_shorts: bool) -> str:
        out_clip = os.path.join(self.temp_dir, f"{job_id}_clip_{scene_num}.mp4")
        is_video = asset_path.endswith(".mp4")
        font_path = self._get_font_path()
        font_param = f":fontfile='{font_path}'" if font_path else ""

        # 1. Generate Timed Phrase Subtitle Filter Chain (TikTok / Shorts Sync Style!)
        phrases = self._chunk_text_to_phrases(spoken_text, max_words=3 if is_shorts else 5, max_chars=18 if is_shorts else 35)
        total_words = sum(len(p.split()) for p in phrases) or 1
        
        font_size = 52 if is_shorts else 40
        y_pos = "(h-h/3.2)" if is_shorts else "(h-h/4.2)"

        drawtext_filters = []
        curr_time = 0.0

        for phrase in phrases:
            p_words = len(phrase.split())
            p_duration = duration * (p_words / total_words)
            start_t = curr_time
            end_t = min(duration, curr_time + p_duration + 0.1)
            curr_time += p_duration

            clean_phrase = (
                phrase.strip()
                .replace("\\", "\\\\")
                .replace(":", "\\:")
                .replace("%", "\\%")
                .replace("'", "")
                .replace('"', "")
                .replace("\n", "\\n")
            )

            # High-contrast bold yellow subtitle with dark pill background & time sync
            dt = f"drawtext=text='{clean_phrase}':enable='between(t,{start_t:.2f},{end_t:.2f})'{font_param}:fontcolor=yellow:fontsize={font_size}:x=(w-text_w)/2:y={y_pos}:box=1:boxcolor=black@0.80:boxborderw=16"
            drawtext_filters.append(dt)

        subtitles_filter_str = ",".join(drawtext_filters)

        # 2. Visual Scale, Crop, and Dynamic Pan/Zoom Motion Filter
        if is_video:
            filter_str = f"[0:v]scale={res_w}:{res_h}:force_original_aspect_ratio=increase,crop={res_w}:{res_h},{subtitles_filter_str}[v]"
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
            # Ken Burns slow zoom effect for images
            filter_str = f"[0:v]scale={res_w*2}:{res_h*2}:force_original_aspect_ratio=increase,crop={res_w*2}:{res_h*2},zoompan=z='min(zoom+0.0015,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:fps=30:s={res_w}x{res_h},{subtitles_filter_str}[v]"
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

    def _concatenate_clips_with_transitions(self, scene_clips: list, scene_durations: list, output_video: str, res_w: int, res_h: int):
        """Concatenates clips using professional xfade visual transitions & acrossfade audio transitions."""
        if len(scene_clips) == 1:
            shutil.copy(scene_clips[0], output_video)
            return

        # Attempt FFmpeg xfade transition pipeline
        try:
            trans_list = ["fade", "wipeleft", "slideleft", "circlecrop", "wiperight", "slidedown"]
            td = 0.35  # 0.35s transition duration

            inputs = []
            filter_parts = []

            for i, clip in enumerate(scene_clips):
                inputs.extend(["-i", clip])

            v_last = "[0:v]"
            a_last = "[0:a]"
            curr_offset = 0.0

            for i in range(len(scene_clips) - 1):
                curr_offset += scene_durations[i] - td
                next_v = f"[v{i+1}]" if i < len(scene_clips) - 2 else "[vout]"
                next_a = f"[a{i+1}]" if i < len(scene_clips) - 2 else "[aout]"
                t_name = trans_list[i % len(trans_list)]

                filter_parts.append(f"{v_last}[{i+1}:v]xfade=transition={t_name}:duration={td:.2f}:offset={curr_offset:.2f}{next_v}")
                filter_parts.append(f"{a_last}[{i+1}:a]acrossfade=d={td:.2f}{next_a}")

                v_last = next_v
                a_last = next_a

            filter_complex = ";".join(filter_parts)

            cmd = ["ffmpeg", "-y"] + inputs + [
                "-filter_complex", filter_complex,
                "-map", "[vout]", "-map", "[aout]",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-b:a", "192k",
                output_video
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[VideoRenderer] xfade transition concatenation succeeded!")
            return
        except Exception as e:
            print(f"[VideoRenderer] xfade transition fallback to standard concat: {e}")

        # Fallback to standard concat demuxer if xfade encounters edge timing issues
        concat_list_path = os.path.join(self.temp_dir, f"concat_fallback_{int(time.time())}.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for c_file in scene_clips:
                clean_path = os.path.abspath(c_file).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        concat_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            output_video
        ]
        subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)

    def _get_or_create_bgm(self, bgm_name: str) -> str:
        if not bgm_name or bgm_name == "auto" or not bgm_name.endswith(".mp3"):
            bgm_name = "tech_ambient.mp3"

        primary_target = os.path.join(self.bgm_dir, bgm_name)
        if os.path.exists(primary_target):
            return primary_target

        # If missing, run the real studio MP3 downloader
        try:
            from create_bgm_library import download_or_generate_bgm
            download_or_generate_bgm()
            if os.path.exists(primary_target):
                return primary_target
        except Exception as e:
            print(f"[VideoRenderer] Error downloading real BGM: {e}")

        # Fallback to default available BGM in directory
        for f in os.listdir(self.bgm_dir):
            if f.endswith(".mp3"):
                return os.path.join(self.bgm_dir, f)

        return primary_target

video_renderer = VideoRenderer()
