import subprocess
import os

font_path = "C\\:/Windows/Fonts/arialbd.ttf"
out = "storage/temp/test_font.mp4"
os.makedirs("storage/temp", exist_ok=True)

cmd = [
    "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1080x1920:d=1",
    "-vf", f"drawtext=fontfile='{font_path}':text='Test Text\\nLine 2':fontcolor=yellow:fontsize=46:x=(w-text_w)/2:y=(h-text_h)/2",
    out
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("STATUS:", res.returncode)
if res.returncode == 0:
    print("SUCCESS! Output file created at:", out)
else:
    print("STDERR:", res.stderr)
