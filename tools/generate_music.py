#!/usr/bin/env python3
"""Generate 8-bit style background music for Bob the Pirate.

Creates dark, foreboding looping background tracks for each level.
"""

import math
import os
import struct
import wave

# Output directory
OUTPUT_DIR = "assets/music"

# Sample rate
SAMPLE_RATE = 44100

# Note frequencies (A4 = 440 Hz tuning) - focusing on minor keys
NOTES = {
    # Octave 2 (deep bass)
    "C2": 65.41, "D2": 73.42, "Eb2": 77.78, "E2": 82.41, "F2": 87.31,
    "G2": 98.00, "Ab2": 103.83, "A2": 110.00, "Bb2": 116.54, "B2": 123.47,
    # Octave 3
    "C3": 130.81, "D3": 146.83, "Eb3": 155.56, "E3": 164.81, "F3": 174.61,
    "G3": 196.00, "Ab3": 207.65, "A3": 220.00, "Bb3": 233.08, "B3": 246.94,
    # Octave 4
    "C4": 261.63, "D4": 293.66, "Eb4": 311.13, "E4": 329.63, "F4": 349.23,
    "G4": 392.00, "Ab4": 415.30, "A4": 440.00, "Bb4": 466.16, "B4": 493.88,
    # Octave 5
    "C5": 523.25, "D5": 587.33, "Eb5": 622.25, "E5": 659.25, "F5": 698.46,
    "G5": 783.99, "Ab5": 830.61, "A5": 880.00, "Bb5": 932.33, "B5": 987.77,
    # Rests
    "R": 0,
}


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_tone(frequency: float, duration: float, wave_type: str = "square",
                  volume: float = 0.2) -> list[int]:
    """Generate a single tone."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE

        if frequency == 0:  # Rest
            value = 0.0
        elif wave_type == "square":
            value = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
        elif wave_type == "triangle":
            value = 2.0 * abs(2.0 * ((frequency * t) % 1.0) - 1.0) - 1.0
        elif wave_type == "sine":
            value = math.sin(2 * math.pi * frequency * t)
        elif wave_type == "sawtooth":
            value = 2.0 * ((frequency * t) % 1.0) - 1.0
        else:
            value = 0.0

        # Simple envelope to avoid clicks
        env = 1.0
        attack = int(0.01 * SAMPLE_RATE)
        release = int(0.02 * SAMPLE_RATE)
        if i < attack:
            env = i / attack
        elif i > num_samples - release:
            env = (num_samples - i) / release

        sample = int(value * volume * env * 32767)
        samples.append(max(-32768, min(32767, sample)))

    return samples


def mix_tracks(tracks: list[list[int]]) -> list[int]:
    """Mix multiple tracks together."""
    if not tracks:
        return []

    max_len = max(len(t) for t in tracks)
    result = []

    for i in range(max_len):
        total = 0
        for track in tracks:
            if i < len(track):
                total += track[i]

        # Clamp to prevent clipping
        result.append(max(-32768, min(32767, total)))

    return result


def save_wav(filename: str, samples: list[int]) -> None:
    """Save samples to a WAV file."""
    filepath = os.path.join(OUTPUT_DIR, filename)

    with wave.open(filepath, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        packed = struct.pack(f"<{len(samples)}h", *samples)
        wav.writeframes(packed)

    print(f"Generated: {filepath}")


def generate_melody(notes_and_durations: list[tuple[str, float]],
                    wave_type: str = "square", volume: float = 0.15) -> list[int]:
    """Generate a melody from a list of (note, duration) tuples."""
    samples = []
    for note, duration in notes_and_durations:
        freq = NOTES.get(note, 0)
        tone = generate_tone(freq, duration, wave_type, volume)
        samples.extend(tone)
    return samples


def generate_bass(notes_and_durations: list[tuple[str, float]],
                  volume: float = 0.12) -> list[int]:
    """Generate a bass line."""
    return generate_melody(notes_and_durations, "triangle", volume)


def generate_drone(note: str, duration: float, volume: float = 0.08) -> list[int]:
    """Generate a low droning note for atmosphere."""
    return generate_melody([(note, duration)], "sawtooth", volume)


def generate_menu_music() -> None:
    """Generate main menu theme - dark, ominous pirate theme."""
    bpm = 85  # Slower, more brooding
    beat = 60 / bpm

    # Dark minor melody - Am
    melody = [
        # Bar 1-2: Ominous opening
        ("A4", beat), ("R", beat / 2), ("E4", beat / 2), ("A4", beat),
        ("G4", beat / 2), ("F4", beat / 2), ("E4", beat * 2),
        # Bar 3-4
        ("A4", beat), ("R", beat / 2), ("C5", beat / 2), ("B4", beat),
        ("A4", beat / 2), ("G4", beat / 2), ("E4", beat * 2),
        # Bar 5-6: Rising tension
        ("D4", beat), ("E4", beat / 2), ("F4", beat / 2), ("G4", beat),
        ("A4", beat / 2), ("G4", beat / 2), ("F4", beat * 2),
        # Bar 7-8: Resolution to minor
        ("E4", beat), ("F4", beat / 2), ("E4", beat / 2), ("D4", beat),
        ("C4", beat / 2), ("D4", beat / 2), ("A3", beat * 2),
    ]

    # Deep, foreboding bass
    bass = [
        ("A2", beat * 4), ("A2", beat * 4),
        ("F2", beat * 4), ("E2", beat * 4),
        ("D2", beat * 4), ("F2", beat * 4),
        ("E2", beat * 4), ("A2", beat * 4),
    ]

    # Low drone for atmosphere
    drone_duration = sum(d for _, d in melody)
    drone = generate_drone("A2", drone_duration, 0.06)

    melody_samples = generate_melody(melody, volume=0.14)
    bass_samples = generate_bass(bass, volume=0.10)

    # Loop
    full_melody = melody_samples * 2
    full_bass = bass_samples * 2
    full_drone = drone * 2

    max_len = max(len(full_melody), len(full_bass), len(full_drone))
    full_melody.extend([0] * (max_len - len(full_melody)))
    full_bass.extend([0] * (max_len - len(full_bass)))
    full_drone.extend([0] * (max_len - len(full_drone)))

    samples = mix_tracks([full_melody, full_bass, full_drone])
    save_wav("menu.wav", samples)


def generate_level1_music() -> None:
    """Generate Port Town theme - uneasy, lurking danger."""
    bpm = 100
    beat = 60 / bpm

    # Dm - uneasy melody
    melody = [
        ("D4", beat), ("R", beat / 2), ("F4", beat / 2), ("A4", beat),
        ("G4", beat / 2), ("F4", beat / 2), ("E4", beat), ("D4", beat),
        ("R", beat / 2), ("A4", beat / 2), ("G4", beat), ("F4", beat / 2),
        ("E4", beat / 2), ("D4", beat * 2),

        ("D4", beat / 2), ("E4", beat / 2), ("F4", beat), ("G4", beat / 2),
        ("A4", beat / 2), ("Bb4", beat), ("A4", beat / 2), ("G4", beat / 2),
        ("F4", beat), ("E4", beat / 2), ("D4", beat / 2), ("E4", beat),
        ("D4", beat * 2),
    ]

    bass = [
        ("D2", beat * 3), ("D3", beat), ("A2", beat * 3), ("A2", beat),
        ("Bb2", beat * 3), ("Bb2", beat), ("A2", beat * 4),
        ("D2", beat * 3), ("D3", beat), ("G2", beat * 3), ("G2", beat),
        ("A2", beat * 3), ("A2", beat), ("D2", beat * 4),
    ]

    melody_samples = generate_melody(melody, volume=0.13)
    bass_samples = generate_bass(bass, volume=0.11)

    full_melody = melody_samples * 2
    full_bass = bass_samples * 2

    max_len = max(len(full_melody), len(full_bass))
    full_melody.extend([0] * (max_len - len(full_melody)))
    full_bass.extend([0] * (max_len - len(full_bass)))

    samples = mix_tracks([full_melody, full_bass])
    save_wav("level1.wav", samples)


def generate_level2_music() -> None:
    """Generate HMS Revenge theme - creaking ship, impending doom."""
    bpm = 90
    beat = 60 / bpm

    # Em - nautical minor
    melody = [
        ("E4", beat), ("G4", beat / 2), ("E4", beat / 2), ("B4", beat),
        ("A4", beat / 2), ("G4", beat / 2), ("E4", beat * 2),
        ("D4", beat), ("E4", beat / 2), ("G4", beat / 2), ("A4", beat),
        ("G4", beat / 2), ("F4", beat / 2), ("E4", beat * 2),

        ("E4", beat / 2), ("F4", beat / 2), ("G4", beat), ("A4", beat / 2),
        ("B4", beat / 2), ("C5", beat), ("B4", beat / 2), ("A4", beat / 2),
        ("G4", beat), ("F4", beat / 2), ("E4", beat / 2), ("D4", beat),
        ("E4", beat * 2),
    ]

    bass = [
        ("E2", beat * 4), ("E2", beat * 4),
        ("C2", beat * 4), ("D2", beat * 4),
        ("E2", beat * 4), ("A2", beat * 4),
        ("C2", beat * 2), ("D2", beat * 2), ("E2", beat * 4),
    ]

    # Creaking drone
    drone_duration = sum(d for _, d in melody)
    drone = generate_drone("E2", drone_duration, 0.05)

    melody_samples = generate_melody(melody, volume=0.13)
    bass_samples = generate_bass(bass, volume=0.10)

    full_melody = melody_samples * 2
    full_bass = bass_samples * 2
    full_drone = drone * 2

    max_len = max(len(full_melody), len(full_bass), len(full_drone))
    full_melody.extend([0] * (max_len - len(full_melody)))
    full_bass.extend([0] * (max_len - len(full_bass)))
    full_drone.extend([0] * (max_len - len(full_drone)))

    samples = mix_tracks([full_melody, full_bass, full_drone])
    save_wav("level2.wav", samples)


def generate_level3_music() -> None:
    """Generate Cliff Fortress theme - relentless, oppressive climb."""
    bpm = 115
    beat = 60 / bpm

    # Cm - intense, driving
    melody = [
        ("C4", beat / 2), ("Eb4", beat / 2), ("G4", beat / 2), ("C5", beat / 2),
        ("Bb4", beat), ("Ab4", beat / 2), ("G4", beat / 2), ("Eb4", beat),
        ("F4", beat / 2), ("G4", beat / 2), ("Ab4", beat), ("G4", beat / 2),
        ("F4", beat / 2), ("Eb4", beat * 2),

        ("C4", beat / 2), ("D4", beat / 2), ("Eb4", beat / 2), ("F4", beat / 2),
        ("G4", beat), ("Ab4", beat / 2), ("Bb4", beat / 2), ("C5", beat),
        ("Bb4", beat / 2), ("Ab4", beat / 2), ("G4", beat), ("F4", beat / 2),
        ("Eb4", beat / 2), ("C4", beat * 2),
    ]

    # Driving bass
    bass = [
        ("C2", beat), ("C2", beat), ("G2", beat), ("G2", beat),
        ("Ab2", beat), ("Ab2", beat), ("Eb2", beat), ("Eb2", beat),
        ("F2", beat), ("F2", beat), ("Ab2", beat), ("Ab2", beat),
        ("G2", beat), ("G2", beat), ("C2", beat * 2),

        ("C2", beat), ("C2", beat), ("Eb2", beat), ("Eb2", beat),
        ("G2", beat), ("G2", beat), ("C3", beat), ("C3", beat),
        ("Ab2", beat), ("Ab2", beat), ("G2", beat), ("G2", beat),
        ("F2", beat), ("F2", beat), ("C2", beat * 2),
    ]

    melody_samples = generate_melody(melody, volume=0.14)
    bass_samples = generate_bass(bass, volume=0.12)

    full_melody = melody_samples * 2
    full_bass = bass_samples * 2

    max_len = max(len(full_melody), len(full_bass))
    full_melody.extend([0] * (max_len - len(full_melody)))
    full_bass.extend([0] * (max_len - len(full_bass)))

    samples = mix_tracks([full_melody, full_bass])
    save_wav("level3.wav", samples)


def generate_miniboss_music() -> None:
    """Generate miniboss (Bosun) theme - brutal, punishing."""
    bpm = 130
    beat = 60 / bpm

    # Gm - aggressive
    melody = [
        ("G4", beat / 2), ("G4", beat / 2), ("Bb4", beat / 2), ("G4", beat / 2),
        ("D5", beat), ("C5", beat / 2), ("Bb4", beat / 2), ("A4", beat),
        ("G4", beat / 2), ("A4", beat / 2), ("Bb4", beat), ("C5", beat / 2),
        ("Bb4", beat / 2), ("G4", beat * 2),

        ("G4", beat / 2), ("Bb4", beat / 2), ("D5", beat / 2), ("F5", beat / 2),
        ("Eb5", beat), ("D5", beat / 2), ("C5", beat / 2), ("Bb4", beat),
        ("A4", beat / 2), ("Bb4", beat / 2), ("G4", beat), ("F4", beat / 2),
        ("G4", beat / 2), ("G4", beat * 2),
    ]

    # Pounding bass
    bass = [
        ("G2", beat / 2), ("G2", beat / 2), ("G2", beat / 2), ("G2", beat / 2),
        ("Bb2", beat / 2), ("Bb2", beat / 2), ("D3", beat / 2), ("D3", beat / 2),
        ("Eb3", beat / 2), ("Eb3", beat / 2), ("D3", beat / 2), ("D3", beat / 2),
        ("G2", beat / 2), ("G2", beat / 2), ("G2", beat),

        ("G2", beat / 2), ("G2", beat / 2), ("Bb2", beat / 2), ("Bb2", beat / 2),
        ("C3", beat / 2), ("C3", beat / 2), ("Eb3", beat / 2), ("Eb3", beat / 2),
        ("D3", beat / 2), ("D3", beat / 2), ("Bb2", beat / 2), ("Bb2", beat / 2),
        ("G2", beat / 2), ("G2", beat / 2), ("G2", beat),
    ]

    melody_samples = generate_melody(melody, volume=0.15)
    bass_samples = generate_bass(bass, volume=0.13)

    full_melody = melody_samples * 2
    full_bass = bass_samples * 2

    max_len = max(len(full_melody), len(full_bass))
    full_melody.extend([0] * (max_len - len(full_melody)))
    full_bass.extend([0] * (max_len - len(full_bass)))

    samples = mix_tracks([full_melody, full_bass])
    save_wav("level4.wav", samples)


def generate_level5_music() -> None:
    """Generate Governor's Mansion theme - sinister elegance, corruption."""
    bpm = 95
    beat = 60 / bpm

    # Fm - dark waltz feeling
    melody = [
        ("F4", beat), ("Ab4", beat / 2), ("C5", beat / 2), ("Bb4", beat),
        ("Ab4", beat / 2), ("G4", beat / 2), ("F4", beat * 2),
        ("Eb4", beat), ("F4", beat / 2), ("G4", beat / 2), ("Ab4", beat),
        ("G4", beat / 2), ("F4", beat / 2), ("Eb4", beat * 2),

        ("F4", beat / 2), ("G4", beat / 2), ("Ab4", beat), ("Bb4", beat / 2),
        ("C5", beat / 2), ("Db5", beat), ("C5", beat / 2), ("Bb4", beat / 2),
        ("Ab4", beat), ("G4", beat / 2), ("F4", beat / 2), ("Eb4", beat),
        ("F4", beat * 2),
    ]

    bass = [
        ("F2", beat * 4), ("Db2", beat * 4),
        ("Eb2", beat * 4), ("C2", beat * 4),
        ("F2", beat * 4), ("Bb2", beat * 4),
        ("C2", beat * 4), ("F2", beat * 4),
    ]

    # Eerie drone
    drone_duration = sum(d for _, d in melody)
    drone = generate_drone("F2", drone_duration, 0.05)

    melody_samples = generate_melody(melody, volume=0.13)
    bass_samples = generate_bass(bass, volume=0.10)

    full_melody = melody_samples * 2
    full_bass = bass_samples * 2
    full_drone = drone * 2

    max_len = max(len(full_melody), len(full_bass), len(full_drone))
    full_melody.extend([0] * (max_len - len(full_melody)))
    full_bass.extend([0] * (max_len - len(full_bass)))
    full_drone.extend([0] * (max_len - len(full_drone)))

    samples = mix_tracks([full_melody, full_bass, full_drone])
    save_wav("level5.wav", samples)


def generate_boss_music() -> None:
    """Generate Admiral boss theme - overwhelming dread, final confrontation."""
    bpm = 140
    beat = 60 / bpm

    # Dm - ultimate darkness
    melody = [
        ("D4", beat / 2), ("D4", beat / 2), ("F4", beat / 2), ("D4", beat / 2),
        ("A4", beat), ("G4", beat / 2), ("F4", beat / 2), ("E4", beat),
        ("D4", beat / 2), ("E4", beat / 2), ("F4", beat), ("G4", beat / 2),
        ("A4", beat / 2), ("D4", beat * 2),

        ("D5", beat / 2), ("C5", beat / 2), ("Bb4", beat / 2), ("A4", beat / 2),
        ("G4", beat), ("F4", beat / 2), ("E4", beat / 2), ("D4", beat),
        ("C4", beat / 2), ("D4", beat / 2), ("E4", beat), ("F4", beat / 2),
        ("E4", beat / 2), ("D4", beat * 2),
    ]

    # Relentless bass
    bass = [
        ("D2", beat / 2), ("D2", beat / 2), ("D2", beat / 2), ("D2", beat / 2),
        ("F2", beat / 2), ("F2", beat / 2), ("A2", beat / 2), ("A2", beat / 2),
        ("Bb2", beat / 2), ("Bb2", beat / 2), ("A2", beat / 2), ("A2", beat / 2),
        ("D2", beat / 2), ("D2", beat / 2), ("D2", beat),

        ("D2", beat / 2), ("D2", beat / 2), ("C2", beat / 2), ("C2", beat / 2),
        ("Bb2", beat / 2), ("Bb2", beat / 2), ("A2", beat / 2), ("A2", beat / 2),
        ("G2", beat / 2), ("G2", beat / 2), ("A2", beat / 2), ("A2", beat / 2),
        ("D2", beat / 2), ("D2", beat / 2), ("D2", beat),
    ]

    # Ominous drone
    drone_duration = sum(d for _, d in melody)
    drone = generate_drone("D2", drone_duration, 0.07)

    melody_samples = generate_melody(melody, volume=0.16)
    bass_samples = generate_bass(bass, volume=0.14)

    full_melody = melody_samples * 2
    full_bass = bass_samples * 2
    full_drone = drone * 2

    max_len = max(len(full_melody), len(full_bass), len(full_drone))
    full_melody.extend([0] * (max_len - len(full_melody)))
    full_bass.extend([0] * (max_len - len(full_bass)))
    full_drone.extend([0] * (max_len - len(full_drone)))

    samples = mix_tracks([full_melody, full_bass, full_drone])
    save_wav("boss.wav", samples)


def generate_victory_music() -> None:
    """Generate victory theme - relief, but bittersweet (minor to major)."""
    bpm = 100
    beat = 60 / bpm

    # Start minor, resolve to major
    melody = [
        # Minor opening
        ("A4", beat), ("C5", beat / 2), ("E5", beat / 2), ("D5", beat),
        ("C5", beat / 2), ("B4", beat / 2), ("A4", beat * 2),
        # Transition
        ("E4", beat), ("G4", beat / 2), ("B4", beat / 2), ("A4", beat),
        ("G4", beat / 2), ("F4", beat / 2), ("E4", beat * 2),
        # Major resolution
        ("C5", beat), ("E5", beat / 2), ("G5", beat / 2), ("F5", beat),
        ("E5", beat / 2), ("D5", beat / 2), ("C5", beat * 2),
        # Triumphant ending
        ("G4", beat), ("C5", beat / 2), ("E5", beat / 2), ("G5", beat * 1.5),
        ("R", beat / 2), ("G5", beat), ("C6", beat * 2),
    ]

    bass = [
        ("A2", beat * 4), ("D2", beat * 4),
        ("E2", beat * 4), ("E2", beat * 4),
        ("C2", beat * 4), ("G2", beat * 4),
        ("C2", beat * 4), ("C2", beat * 4),
    ]

    melody_samples = generate_melody(melody, volume=0.14)
    bass_samples = generate_bass(bass, volume=0.11)

    max_len = max(len(melody_samples), len(bass_samples))
    melody_samples.extend([0] * (max_len - len(melody_samples)))
    bass_samples.extend([0] * (max_len - len(bass_samples)))

    samples = mix_tracks([melody_samples, bass_samples])
    save_wav("victory.wav", samples)


def main():
    """Generate all background music tracks."""
    print("Generating dark 8-bit background music...")
    ensure_output_dir()

    generate_menu_music()
    generate_level1_music()
    generate_level2_music()
    generate_level3_music()
    generate_miniboss_music()
    generate_level5_music()
    generate_boss_music()
    generate_victory_music()

    print(f"\nGenerated {len(os.listdir(OUTPUT_DIR))} music files in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
