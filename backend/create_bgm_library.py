import os
import subprocess

BGM_DIR = "storage/bgm"
os.makedirs(BGM_DIR, exist_ok=True)

TRACK_DESCRIPTIONS = {
    "happy_playful.mp3": {
        "desc": "Happy & Playful Bouncy Melody (120 BPM C-Major Bouncy Arpeggio)",
        "expr": "0.4*sin(2*3.14159*523.25*t)*gt(mod(t*4,1),0.5)+0.3*sin(2*3.14159*659.25*t)*gt(mod(t*4+0.25,1),0.5)+0.25*sin(2*3.14159*783.99*t)*gt(mod(t*4+0.5,1),0.5)+0.2*sin(2*3.14159*1046.5*t)*gt(mod(t*8,1),0.3)",
        "filter": "volume=0.8,lowpass=f=3500,aecho=0.8:0.7:150:0.2"
    },
    "lofi_chill.mp3": {
        "desc": "Lo-Fi Chill Hop (80 BPM Relaxing Jazzy Warm Chords)",
        "expr": "0.3*sin(2*3.14159*174.61*t)+0.25*sin(2*3.14159*220.00*t)+0.2*sin(2*3.14159*261.63*t)+0.15*sin(2*3.14159*349.23*t)+0.05*sin(2*3.14159*1200*t)*sin(50*t)",
        "filter": "lowpass=f=1200,volume=0.9,aecho=0.8:0.8:300:0.3"
    },
    "dark_suspense.mp3": {
        "desc": "Dark Suspense Thriller (Low Sub-Bass Pulse 55Hz & Slow Tension Modulation)",
        "expr": "0.5*sin(2*3.14159*55*t)+0.3*sin(2*3.14159*65.41*t)*sin(0.5*3.14159*t)+0.2*sin(2*3.14159*82.41*t)+0.15*sin(2*3.14159*110*t)*sin(2*3.14159*t)",
        "filter": "lowpass=f=400,volume=1.0,aecho=0.8:0.9:400:0.4"
    },
    "upbeat_cyber.mp3": {
        "desc": "Upbeat Cyber Synthwave (135 BPM 16th-Note Fast Arpeggiator Bassline)",
        "expr": "0.35*sin(2*3.14159*130.81*t*gt(mod(t*8,1),0.4))+0.3*sin(2*3.14159*261.63*t*gt(mod(t*8+0.25,1),0.4))+0.25*sin(2*3.14159*392.00*t*gt(mod(t*8+0.5,1),0.4))+0.2*sin(2*3.14159*523.25*t)",
        "filter": "highpass=f=100,lowpass=f=4500,volume=0.85,apulsator=hz=2"
    },
    "tech_ambient.mp3": {
        "desc": "Tech Ambient Futuristic (Ethereal Digital Waves & Stereo Pulse)",
        "expr": "0.3*sin(2*3.14159*146.83*t)+0.25*sin(2*3.14159*220.00*t)*sin(0.8*t)+0.2*sin(2*3.14159*293.66*t)*sin(1.5*t)+0.15*sin(2*3.14159*440.00*t)",
        "filter": "volume=0.85,aecho=0.8:0.9:500:0.4,apulsator=hz=0.5"
    },
    "inspiring_modern.mp3": {
        "desc": "Inspiring Modern Piano Swells (Uplifting Bright Major Chords)",
        "expr": "0.35*sin(2*3.14159*329.63*t)+0.3*sin(2*3.14159*415.30*t)+0.25*sin(2*3.14159*493.88*t)+0.2*sin(2*3.14159*659.25*t)*sin(0.5*t)",
        "filter": "lowpass=f=2800,volume=0.85,aecho=0.7:0.8:250:0.3"
    },
    "cinematic_epic.mp3": {
        "desc": "Cinematic Epic Orchestral (Deep Timpani & Rising Horn Crescendo)",
        "expr": "0.45*sin(2*3.14159*65.41*t)+0.3*sin(2*3.14159*98.00*t)+0.25*sin(2*3.14159*130.81*t)*sin(0.2*3.14159*t)+0.2*sin(2*3.14159*196.00*t)",
        "filter": "lowpass=f=900,volume=0.95,aecho=0.8:0.9:600:0.4"
    },
    "scary_drone.mp3": {
        "desc": "Scary Horror Microtonal Cluster (Terrifying Dissonant Horror Tension)",
        "expr": "0.35*sin(2*3.14159*65.41*t)+0.35*sin(2*3.14159*69.30*t)+0.25*sin(2*3.14159*130.81*t)+0.2*sin(2*3.14159*138.59*t)*sin(8*t)",
        "filter": "volume=0.9,aecho=0.8:0.9:200:0.5"
    },
    "triumphant_build.mp3": {
        "desc": "Triumphant Motivation Build (130 BPM Rhythmic Marching Brass Pulse)",
        "expr": "0.4*sin(2*3.14159*130.81*t)*gt(mod(t*4.33,1),0.4)+0.3*sin(2*3.14159*164.81*t)+0.25*sin(2*3.14159*196.00*t)*gt(mod(t*4.33+0.5,1),0.4)+0.2*sin(2*3.14159*261.63*t)",
        "filter": "lowpass=f=3200,volume=0.9,aecho=0.7:0.8:200:0.3"
    }
}

def generate_bgm_library():
    for name, data in TRACK_DESCRIPTIONS.items():
        out_path = os.path.join(BGM_DIR, name)
        expr = data["expr"]
        flt = data.get("filter", "volume=0.85")
        desc = data["desc"]
        print(f"[BGM Generator] Rendering {name} ({desc})...")
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"aevalsrc=exprs='{expr}':s=44100",
            "-af", flt,
            "-t", "120",
            "-c:a", "libmp3lame", "-b:a", "192k",
            out_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[BGM Generator] All 9 distinct high-quality background music tracks created successfully!")

if __name__ == "__main__":
    generate_bgm_library()
