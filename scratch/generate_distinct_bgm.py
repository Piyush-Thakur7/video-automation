import os
import math
import struct
import wave
import subprocess
import numpy as np

OUTPUT_DIR = "storage/bgm"
os.makedirs(OUTPUT_DIR, exist_ok=True)
SAMPLE_RATE = 44100
DURATION = 90 # 90 seconds loop

def note_to_freq(note_str):
    notes = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    letter = note_str[:-1]
    octave = int(note_str[-1])
    n = notes[letter] + (octave + 1) * 12
    return 440.0 * (2.0 ** ((n - 69) / 12.0))

def generate_track_audio(genre):
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    audio = np.zeros_like(t)

    if genre == "happy_playful":
        # 120 BPM bouncy arpeggio (C Major: C4, E4, G4, C5, G4, E4)
        bpm = 120
        beat_sec = 60.0 / bpm
        notes = [note_to_freq(n) for n in ["C4", "E4", "G4", "C5", "G4", "E4", "F4", "A4"]]
        num_beats = int(DURATION / (beat_sec / 2))
        for i in range(num_beats):
            start = int(i * (beat_sec / 2) * SAMPLE_RATE)
            end = int((i + 1) * (beat_sec / 2) * SAMPLE_RATE)
            if start >= len(t): break
            freq = notes[i % len(notes)]
            t_sub = t[start:end] - t[start]
            decay = np.exp(-t_sub * 8.0)
            tone = (np.sin(2 * np.pi * freq * t_sub) + 0.3 * np.sin(2 * np.pi * freq * 2 * t_sub)) * decay
            audio[start:min(end, len(audio))] += tone[:len(audio[start:end])]
        # Add bouncy bass
        bass_freqs = [note_to_freq("C3"), note_to_freq("F3"), note_to_freq("G3"), note_to_freq("C3")]
        for i in range(int(DURATION / beat_sec)):
            start = int(i * beat_sec * SAMPLE_RATE)
            end = int((i + 1) * beat_sec * SAMPLE_RATE)
            if start >= len(t): break
            bfreq = bass_freqs[i % len(bass_freqs)]
            t_sub = t[start:end] - t[start]
            decay = np.exp(-t_sub * 3.0)
            btone = 0.4 * np.sin(2 * np.pi * bfreq * t_sub) * decay
            audio[start:min(end, len(audio))] += btone[:len(audio[start:end])]

    elif genre == "dark_suspense":
        # 60 BPM low D minor drone (D2, F2, A2) with pulsing sub-bass tremolo
        f_d2 = note_to_freq("D2")
        f_f2 = note_to_freq("F2")
        f_a2 = note_to_freq("A2")
        pulse = 0.5 * (1.0 + np.sin(2 * np.pi * 0.25 * t))
        audio += 0.4 * np.sin(2 * np.pi * f_d2 * t) * pulse
        audio += 0.25 * np.sin(2 * np.pi * f_f2 * t) * (1.0 - pulse)
        audio += 0.2 * np.sin(2 * np.pi * f_a2 * t)
        # Add eerie high pitch frequency modulation
        mod = np.sin(2 * np.pi * 0.1 * t) * 20.0
        audio += 0.1 * np.sin(2 * np.pi * (1200 + mod) * t)

    elif genre == "cinematic_epic":
        # 90 BPM A minor chord progression (A2 -> F2 -> C3 -> G2) with brass swell
        chord_dur = 4.0 # 4 seconds per chord
        chords = [
            [note_to_freq("A2"), note_to_freq("C3"), note_to_freq("E3"), note_to_freq("A3")],
            [note_to_freq("F2"), note_to_freq("A2"), note_to_freq("C3"), note_to_freq("F3")],
            [note_to_freq("C3"), note_to_freq("E3"), note_to_freq("G3"), note_to_freq("C4")],
            [note_to_freq("G2"), note_to_freq("B2"), note_to_freq("D3"), note_to_freq("G3")]
        ]
        num_chords = int(DURATION / chord_dur)
        for i in range(num_chords):
            start = int(i * chord_dur * SAMPLE_RATE)
            end = int((i + 1) * chord_dur * SAMPLE_RATE)
            if start >= len(t): break
            c_freqs = chords[i % len(chords)]
            t_sub = t[start:end] - t[start]
            # Swell envelope
            env = np.sin(np.pi * (t_sub / chord_dur)) ** 2
            chord_signal = sum(np.sin(2 * np.pi * f * t_sub) + 0.5 * np.sin(2 * np.pi * f * 2 * t_sub) for f in c_freqs)
            audio[start:min(end, len(audio))] += (0.2 * chord_signal * env)[:len(audio[start:end])]

    elif genre == "inspiring_modern":
        # E Major ambient piano chords (E3 -> B2 -> C#3 -> A2) with soft pad
        chord_dur = 3.0
        chords = [
            [note_to_freq("E3"), note_to_freq("G#3"), note_to_freq("B3")],
            [note_to_freq("B2"), note_to_freq("D#3"), note_to_freq("F#3")],
            [note_to_freq("C#3"), note_to_freq("E3"), note_to_freq("G#3")],
            [note_to_freq("A2"), note_to_freq("C#3"), note_to_freq("E3")]
        ]
        num_chords = int(DURATION / chord_dur)
        for i in range(num_chords):
            start = int(i * chord_dur * SAMPLE_RATE)
            end = int((i + 1) * chord_dur * SAMPLE_RATE)
            if start >= len(t): break
            c_freqs = chords[i % len(chords)]
            t_sub = t[start:end] - t[start]
            env = np.exp(-t_sub * 0.8)
            signal = sum(np.sin(2 * np.pi * f * t_sub) for f in c_freqs)
            audio[start:min(end, len(audio))] += (0.25 * signal * env)[:len(audio[start:end])]

    elif genre == "lofi_chill":
        # 80 BPM G Major chillhop chords (Gmaj7 -> Em7 -> Am7 -> D7)
        chord_dur = 3.75
        chords = [
            [note_to_freq("G3"), note_to_freq("B3"), note_to_freq("D4"), note_to_freq("F#4")],
            [note_to_freq("E3"), note_to_freq("G3"), note_to_freq("B3"), note_to_freq("D4")],
            [note_to_freq("A3"), note_to_freq("C4"), note_to_freq("E4"), note_to_freq("G4")],
            [note_to_freq("D3"), note_to_freq("F#3"), note_to_freq("A3"), note_to_freq("C4")]
        ]
        num_chords = int(DURATION / chord_dur)
        for i in range(num_chords):
            start = int(i * chord_dur * SAMPLE_RATE)
            end = int((i + 1) * chord_dur * SAMPLE_RATE)
            if start >= len(t): break
            c_freqs = chords[i % len(chords)]
            t_sub = t[start:end] - t[start]
            env = np.exp(-t_sub * 0.5) * (1.0 + 0.05 * np.sin(2 * np.pi * 5.0 * t_sub)) # vinyl vibrato
            signal = sum(0.2 * np.sin(2 * np.pi * f * t_sub) for f in c_freqs)
            audio[start:min(end, len(audio))] += (signal * env)[:len(audio[start:end])]

    elif genre == "scary_drone":
        # Disharmonious cluster drone (F#2, G2, C3) with slow microtonal pitch bending
        f1 = note_to_freq("F#2")
        f2 = note_to_freq("G2")
        f3 = note_to_freq("C3")
        wobble = np.sin(2 * np.pi * 0.05 * t) * 8.0
        audio += 0.35 * np.sin(2 * np.pi * (f1 + wobble) * t)
        audio += 0.35 * np.sin(2 * np.pi * (f2 - wobble) * t)
        audio += 0.25 * np.sin(2 * np.pi * f3 * t)
        # Random creepy clicks/spikes
        np.random.seed(42)
        spikes = np.random.choice([0, 1], size=len(t), p=[0.9999, 0.0001]) * np.random.uniform(-0.5, 0.5, size=len(t))
        audio += spikes

    elif genre == "tech_ambient":
        # 128 BPM Arpeggiated 16th note synth pulse (F#3, C#4, G#4, D#5)
        bpm = 128
        step_sec = 60.0 / bpm / 4.0 # 16th note
        notes = [note_to_freq(n) for n in ["F#3", "C#4", "G#4", "D#5", "A#4", "F#4", "C#4", "G#3"]]
        num_steps = int(DURATION / step_sec)
        for i in range(num_steps):
            start = int(i * step_sec * SAMPLE_RATE)
            end = int((i + 1) * step_sec * SAMPLE_RATE)
            if start >= len(t): break
            freq = notes[i % len(notes)]
            t_sub = t[start:end] - t[start]
            decay = np.exp(-t_sub * 25.0)
            tone = 0.3 * (2.0 * np.abs(2.0 * (freq * t_sub - np.floor(0.5 + freq * t_sub))) - 1.0) * decay # Triangle wave
            audio[start:min(end, len(audio))] += tone[:len(audio[start:end])]

    elif genre == "triumphant_build":
        # C Major rising orchestral chord progression (C3 -> D3 -> F3 -> G3 -> C4)
        chords = [
            [note_to_freq("C3"), note_to_freq("E3"), note_to_freq("G3")],
            [note_to_freq("D3"), note_to_freq("F#3"), note_to_freq("A3")],
            [note_to_freq("F3"), note_to_freq("A3"), note_to_freq("C4")],
            [note_to_freq("G3"), note_to_freq("B3"), note_to_freq("D4")],
            [note_to_freq("C4"), note_to_freq("E4"), note_to_freq("G4")]
        ]
        chord_dur = 2.5
        num_chords = int(DURATION / chord_dur)
        for i in range(num_chords):
            start = int(i * chord_dur * SAMPLE_RATE)
            end = int((i + 1) * chord_dur * SAMPLE_RATE)
            if start >= len(t): break
            c_freqs = chords[i % len(chords)]
            t_sub = t[start:end] - t[start]
            env = np.exp(-t_sub * 0.4)
            signal = sum(0.25 * np.sin(2 * np.pi * f * t_sub) + 0.1 * np.sin(2 * np.pi * f * 3 * t_sub) for f in c_freqs)
            audio[start:min(end, len(audio))] += (signal * env)[:len(audio[start:end])]

    elif genre == "upbeat_cyber":
        # 135 BPM Synthwave Bassline & Sawtooth Melody (A minor)
        bpm = 135
        step_sec = 60.0 / bpm / 2.0 # 8th note
        bass_notes = [note_to_freq(n) for n in ["A2", "A2", "C3", "C3", "F2", "F2", "G2", "G2"]]
        num_steps = int(DURATION / step_sec)
        for i in range(num_steps):
            start = int(i * step_sec * SAMPLE_RATE)
            end = int((i + 1) * step_sec * SAMPLE_RATE)
            if start >= len(t): break
            freq = bass_notes[i % len(bass_notes)]
            t_sub = t[start:end] - t[start]
            decay = np.exp(-t_sub * 12.0)
            # Sawtooth synth wave
            saw = 0.3 * (2.0 * (freq * t_sub - np.floor(0.5 + freq * t_sub))) * decay
            audio[start:min(end, len(audio))] += saw[:len(audio[start:end])]

    # Normalize audio to -3dB peak
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = (audio / max_val) * 0.7

    return audio

GENRES = [
    "happy_playful",
    "dark_suspense",
    "cinematic_epic",
    "inspiring_modern",
    "lofi_chill",
    "scary_drone",
    "tech_ambient",
    "triumphant_build",
    "upbeat_cyber"
]

print("Generating 9 TRULY DISTINCT background music tracks...")
for g in GENRES:
    wav_file = f"storage/bgm/{g}.wav"
    mp3_file = f"storage/bgm/{g}.mp3"
    audio_data = generate_track_audio(g)
    
    # Write 16-bit PCM WAV
    audio_int16 = (audio_data * 32767).astype(np.int16)
    with wave.open(wav_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
        
    # Convert to MP3 via FFmpeg
    subprocess.run(["ffmpeg", "-y", "-i", wav_file, "-c:a", "libmp3lame", "-b:a", "192k", mp3_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(wav_file)
    print(f"OK Generated {g}.mp3 ({os.path.getsize(mp3_file)} bytes)")

print("\nALL 9 BGM TRACKS RE-GENERATED WITH 100% UNIQUE SOUNDS & FREQUENCIES!")
