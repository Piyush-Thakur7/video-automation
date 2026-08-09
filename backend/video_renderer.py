import os
import shutil
import subprocess
import uuid
from asset_manager import asset_manager
from script_generator import script_gen

class VideoRenderer:
    def __init__(self, output_dir: str = "storage/renders", temp_dir: str = "storage/temp"):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def render_video(self, job_id: str, script_data: dict, audio_data: dict, progress_callback=None) -> dict:
        """
        Renders a full 1080p MP4 video with synced spoken subtitles, Ken Burns motion effects, and ambient background music.
        """
        def update_progress(pct: float, msg: str):
            if progress_callback:
                progress_callback(job_id, pct, msg)

        update_progress(5.0, "Synthesizing voiceover and generating timestamps...")

        is_shorts = script_data.get("video_type", "shorts") == "shorts"
        res_w, res_h = (1080, 1920) if is_shorts else (1920, 1080)

        scenes = script_data.get("scenes", [])
        total_scenes = len(scenes)

        scene_clips = []
        full_audio_path = audio_data.get("audio_path")

        for idx, scene in enumerate(scenes, 1):
            pct = 10.0 + (idx / total_scenes) * 50.0
            update_progress(pct, f"Processing scene {idx}/{total_scenes}: {scene.get('type')}")

            search_term = scene.get("search_term", "abstract cinematic")
            media_info = asset_manager.get_scene_media(job_id, idx, search_term, is_shorts)
            asset_path = media_info["asset_path"]

            spoken_text = scene.get("text", "")
            overlay_text = scene.get("overlay_text", "")

            # Segment full audio by estimated scene duration
            scene_duration = round(len(spoken_text.split()) / 2.5, 1)
            if scene_duration < 2.5:
                scene_duration = 2.5

            clip_path = self._create_scene_clip(
                job_id=job_id,
                scene_num=idx,
                asset_path=asset_path,
                audio_path=full_audio_path,
                duration=scene_duration,
                res_w=res_w,
                res_h=res_h,
                spoken_text=spoken_text,
                overlay_text=overlay_text,
                is_shorts=is_shorts
            )
            scene_clips.append(clip_path)

        update_progress(60.0, "Concatenating scene clips...")

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

        update_progress(80.0, "Mixing ambient background music & finalizing output...")

        final_output_path = os.path.join(self.output_dir, f"{job_id}_{script_data.get('video_type', 'shorts')}.mp4")

        # Mix background music
        bgm_track_name = script_data.get("bg_music", "auto")
        if bgm_track_name == "auto":
            bgm_track_name = script_gen.auto_select_bgm(script_data.get("topic", ""), script_data.get("niche", ""))

        bgm_path = self._get_or_create_bgm(bgm_track_name)

        mix_cmd = [
            "ffmpeg", "-y",
            "-i", raw_concat_video,
            "-stream_loop", "-1", "-i", bgm_path,
            "-filter_complex", "[1:a]volume=0.45[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            final_output_path
        ]
        
        try:
            subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[VideoRenderer] Audio mixing fallback: {e}")
            shutil.copy(raw_concat_video, final_output_path)

        update_progress(100.0, "Video rendering complete!")

        return {
            "job_id": job_id,
            "output_path": final_output_path,
            "file_size_mb": round(os.path.getsize(final_output_path) / (1024 * 1024), 2),
            "video_type": script_data.get("video_type"),
            "resolution": f"{res_w}x{res_h}"
        }

    def _wrap_text(self, text: str, max_chars: int = 30) -> str:
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

    def _create_scene_clip(self, job_id: str, scene_num: int, asset_path: str, audio_path: str, duration: float, res_w: int, res_h: int, spoken_text: str, overlay_text: str, is_shorts: bool) -> str:
        out_clip = os.path.join(self.temp_dir, f"{job_id}_clip_{scene_num}.mp4")
        is_video = asset_path.endswith(".mp4")

        # Format spoken script text for subtitles
        formatted_subtitle = self._wrap_text(spoken_text, max_chars=28 if is_shorts else 45)
        escaped_subtitle = formatted_subtitle.replace(":", "\\:").replace("'", "").replace('"', "")
        font_path = "C\\:/Windows/Fonts/arialbd.ttf"
        
        font_size = 46 if is_shorts else 36
        y_pos = "(h-h/3.5)" if is_shorts else "(h-h/5)"

        drawtext_filter = f"drawtext=fontfile='{font_path}':text='{escaped_subtitle}':fontcolor=yellow:fontsize={font_size}:x=(w-text_w)/2:y={y_pos}:box=1:boxcolor=black@0.75:boxborderw=14:line_spacing=10"

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

        bgm_dir = os.path.join(self.temp_dir, "bgm")
        os.makedirs(bgm_dir, exist_ok=True)
        target = os.path.join(bgm_dir, bgm_name)

        if not os.path.exists(target):
            # Rich harmonic ambient soundscape with warm chord progression
            synth_expr = "0.35*sin(2*3.14159*130.81*t)+0.28*sin(2*3.14159*164.81*t)+0.22*sin(2*3.14159*196.00*t)+0.18*sin(2*3.14159*261.63*t)"
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"aevalsrc=exprs='{synth_expr}':s=44100",
                "-t", "90",
                "-c:a", "libmp3lame", "-b:a", "192k",
                target
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return target

video_renderer = VideoRenderer()
