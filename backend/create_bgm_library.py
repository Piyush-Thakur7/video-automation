import os
import subprocess

BGM_DIR = "storage/bgm"
os.makedirs(BGM_DIR, exist_ok=True)

TRACK_SYNTHS = {
    "dark_suspense.mp3": "0.35*sin(2*3.14159*110*t)+0.25*sin(2*3.14159*130.81*t)+0.2*sin(2*3.14159*164.81*t)+0.15*sin(2*3.14159*220*t)",
    "upbeat_cyber.mp3": "0.3*sin(2*3.14159*261.63*t)+0.25*sin(2*3.14159*329.63*t)+0.2*sin(2*3.14159*392.00*t)+0.15*sin(2*3.14159*523.25*t)",
    "tech_ambient.mp3": "0.3*sin(2*3.14159*146.83*t)+0.25*sin(2*3.14159*220.00*t)+0.2*sin(2*3.14159*293.66*t)+0.15*sin(2*3.14159*440.00*t)",
    "inspiring_modern.mp3": "0.35*sin(2*3.14159*174.61*t)+0.25*sin(2*3.14159*220.00*t)+0.2*sin(2*3.14159*261.63*t)+0.15*sin(2*3.14159*349.23*t)",
    "cinematic_epic.mp3": "0.4*sin(2*3.14159*98.00*t)+0.3*sin(2*3.14159*146.83*t)+0.2*sin(2*3.14159*196.00*t)+0.15*sin(2*3.14159*293.66*t)",
    "scary_drone.mp3": "0.4*sin(2*3.14159*65.41*t)+0.25*sin(2*3.14159*69.30*t)+0.2*sin(2*3.14159*130.81*t)+0.15*sin(2*3.14159*138.59*t)",
    "triumphant_build.mp3": "0.35*sin(2*3.14159*130.81*t)+0.3*sin(2*3.14159*164.81*t)+0.25*sin(2*3.14159*196.00*t)+0.2*sin(2*3.14159*261.63*t)"
}

def generate_bgm_library():
    for name, expr in TRACK_SYNTHS.items():
        out_path = os.path.join(BGM_DIR, name)
        if not os.path.exists(out_path):
            print(f"[BGM Generator] Rendering {name}...")
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"aevalsrc=exprs='{expr}':s=44100",
                "-t", "120",
                "-c:a", "libmp3lame", "-b:a", "192k",
                out_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[BGM Generator] All 7 background music tracks created successfully!")

if __name__ == "__main__":
    generate_bgm_library()
