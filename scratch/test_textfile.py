import sys, os, subprocess
sys.path.append("backend")
from video_renderer import video_renderer

print("Testing textfile FFmpeg subtitle rendering...")
raw_text = "Did you know? 100% of human brains react to '50%' more signals: amazing facts!"
wrapped = video_renderer._wrap_text(raw_text, max_chars=24)

sub_txt_path = "storage/temp/test_sub.txt"
os.makedirs("storage/temp", exist_ok=True)
with open(sub_txt_path, "w", encoding="utf-8") as f:
    f.write(wrapped)

escaped_text = wrapped.replace(":", "\\:").replace("%", "\\%").replace("'", "").replace('"', "").replace("\n", "\\n")
font_path = "C\\:/Windows/Fonts/arialbd.ttf"

cmd = [
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", "color=c=blue:s=1080x1920:d=3",
    "-filter_complex", f"[0:v]drawtext=text='{escaped_text}':fontfile='{font_path}':fontcolor=yellow:fontsize=46:x=(w-text_w)/2:y=(h-h/3.2):box=1:boxcolor=black@0.75:boxborderw=14:line_spacing=10[v]",
    "-map", "[v]",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
    "storage/temp/test_textfile_clip.mp4"
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("STATUS:", res.returncode)
if res.returncode == 0:
    print("SUCCESS! Subtitle textfile clip created successfully!")
    if os.path.exists("storage/temp/test_textfile_clip.mp4"):
        os.remove("storage/temp/test_textfile_clip.mp4")
else:
    print("STDERR:", res.stderr[-400:])
