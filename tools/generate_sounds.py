#!/usr/bin/env python3
"""Generate 8-bit style sound effects for Bob the Pirate.

Uses pygame's sound synthesis capabilities to create retro-style sounds.
"""

import math
import os
import struct
import wave

# Output directory
OUTPUT_DIR = "assets/sounds"


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_wave(frequency: float, duration: float, sample_rate: int = 44100,
                  wave_type: str = "square", volume: float = 0.3) -> list[int]:
    """
    Generate a waveform.

    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Samples per second
        wave_type: "square", "sine", "sawtooth", "triangle", or "noise"
        volume: Volume multiplier (0.0 to 1.0)

    Returns:
        List of 16-bit signed integer samples
    """
    import random

    num_samples = int(sample_rate * duration)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate

        if wave_type == "square":
            # Square wave
            value = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
        elif wave_type == "sine":
            value = math.sin(2 * math.pi * frequency * t)
        elif wave_type == "sawtooth":
            value = 2.0 * ((frequency * t) % 1.0) - 1.0
        elif wave_type == "triangle":
            value = 2.0 * abs(2.0 * ((frequency * t) % 1.0) - 1.0) - 1.0
        elif wave_type == "noise":
            value = random.uniform(-1.0, 1.0)
        else:
            value = 0.0

        # Apply volume and convert to 16-bit integer
        sample = int(value * volume * 32767)
        sample = max(-32768, min(32767, sample))
        samples.append(sample)

    return samples


def apply_envelope(samples: list[int], attack: float = 0.01, decay: float = 0.1,
                   sustain: float = 0.7, release: float = 0.1,
                   sample_rate: int = 44100) -> list[int]:
    """Apply ADSR envelope to samples."""
    total = len(samples)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total - attack_samples - decay_samples - release_samples

    if sustain_samples < 0:
        sustain_samples = 0

    result = []
    for i, sample in enumerate(samples):
        if i < attack_samples:
            # Attack phase
            env = i / attack_samples if attack_samples > 0 else 1.0
        elif i < attack_samples + decay_samples:
            # Decay phase
            progress = (i - attack_samples) / decay_samples if decay_samples > 0 else 0
            env = 1.0 - (1.0 - sustain) * progress
        elif i < attack_samples + decay_samples + sustain_samples:
            # Sustain phase
            env = sustain
        else:
            # Release phase
            progress = (i - attack_samples - decay_samples - sustain_samples) / release_samples
            env = sustain * (1.0 - progress)

        result.append(int(sample * env))

    return result


def save_wav(filename: str, samples: list[int], sample_rate: int = 44100) -> None:
    """Save samples to a WAV file."""
    filepath = os.path.join(OUTPUT_DIR, filename)

    with wave.open(filepath, "w") as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)

        # Pack samples as 16-bit signed integers
        packed = struct.pack(f"<{len(samples)}h", *samples)
        wav.writeframes(packed)

    print(f"Generated: {filepath}")


def generate_jump() -> None:
    """Generate jump sound - rising pitch."""
    samples = []
    duration = 0.15
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Rising frequency from 200 to 600 Hz
        freq = 200 + (400 * t / duration)
        value = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        sample = int(value * 0.25 * 32767)
        samples.append(sample)

    samples = apply_envelope(samples, attack=0.01, decay=0.05, sustain=0.5, release=0.05)
    save_wav("jump.wav", samples)


def generate_land() -> None:
    """Generate landing sound - short thud."""
    samples = []
    duration = 0.08
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Low frequency with quick decay
        freq = 100 - (50 * t / duration)
        value = math.sin(2 * math.pi * freq * t)
        # Add some noise
        import random
        value += random.uniform(-0.3, 0.3)
        sample = int(value * 0.3 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.005, decay=0.07, sustain=0.0, release=0.01)
    save_wav("land.wav", samples)


def generate_slash() -> None:
    """Generate sword slash sound - sweeping noise."""
    import random

    samples = []
    duration = 0.12
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # High-pitched sweep with noise
        freq = 800 - (600 * t / duration)
        wave_val = math.sin(2 * math.pi * freq * t) * 0.4
        noise_val = random.uniform(-0.6, 0.6)
        value = wave_val + noise_val
        sample = int(value * 0.25 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.01, decay=0.08, sustain=0.2, release=0.03)
    save_wav("slash.wav", samples)


def generate_hit() -> None:
    """Generate hit/impact sound."""
    import random

    samples = []
    duration = 0.1
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Square wave with some noise
        freq = 150
        square = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        noise = random.uniform(-0.5, 0.5)
        value = square * 0.5 + noise * 0.5
        sample = int(value * 0.35 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.005, decay=0.08, sustain=0.1, release=0.02)
    save_wav("hit.wav", samples)


def generate_hurt() -> None:
    """Generate player hurt sound - descending tone."""
    samples = []
    duration = 0.25
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Descending frequency
        freq = 400 - (200 * t / duration)
        value = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        sample = int(value * 0.3 * 32767)
        samples.append(sample)

    samples = apply_envelope(samples, attack=0.01, decay=0.1, sustain=0.5, release=0.1)
    save_wav("hurt.wav", samples)


def generate_death() -> None:
    """Generate death sound - dramatic descending."""
    samples = []
    duration = 0.5
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Multiple descending frequencies
        freq1 = 300 - (250 * t / duration)
        freq2 = 200 - (150 * t / duration)
        val1 = 1.0 if math.sin(2 * math.pi * freq1 * t) >= 0 else -1.0
        val2 = math.sin(2 * math.pi * freq2 * t)
        value = val1 * 0.5 + val2 * 0.5
        sample = int(value * 0.3 * 32767)
        samples.append(sample)

    samples = apply_envelope(samples, attack=0.02, decay=0.2, sustain=0.4, release=0.2)
    save_wav("death.wav", samples)


def generate_coin() -> None:
    """Generate coin collect sound - bright chime."""
    samples = []
    duration = 0.15
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Two harmonious frequencies
        freq1 = 880
        freq2 = 1320  # Perfect fifth
        val1 = math.sin(2 * math.pi * freq1 * t)
        val2 = math.sin(2 * math.pi * freq2 * t)
        value = val1 * 0.5 + val2 * 0.3
        sample = int(value * 0.25 * 32767)
        samples.append(sample)

    samples = apply_envelope(samples, attack=0.01, decay=0.08, sustain=0.3, release=0.06)
    save_wav("coin.wav", samples)


def generate_treasure() -> None:
    """Generate treasure chest collect sound - triumphant."""
    samples = []
    duration = 0.3
    sample_rate = 44100

    # Arpeggio effect
    notes = [523, 659, 784, 1047]  # C5, E5, G5, C6
    note_duration = duration / len(notes)

    for note_idx, freq in enumerate(notes):
        start_sample = int(note_idx * note_duration * sample_rate)
        end_sample = int((note_idx + 1) * note_duration * sample_rate)

        for i in range(start_sample, end_sample):
            t = i / sample_rate
            value = math.sin(2 * math.pi * freq * t)
            sample = int(value * 0.3 * 32767)
            samples.append(sample)

    samples = apply_envelope(samples, attack=0.01, decay=0.1, sustain=0.6, release=0.1)
    save_wav("treasure.wav", samples)


def generate_powerup() -> None:
    """Generate power-up collect sound."""
    samples = []
    duration = 0.4
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Rising pitch with shimmer
        freq = 400 + (600 * t / duration)
        freq2 = freq * 1.5
        val1 = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        val2 = math.sin(2 * math.pi * freq2 * t)
        value = val1 * 0.4 + val2 * 0.3
        sample = int(value * 0.25 * 32767)
        samples.append(sample)

    samples = apply_envelope(samples, attack=0.02, decay=0.15, sustain=0.5, release=0.15)
    save_wav("powerup.wav", samples)


def generate_enemy_death() -> None:
    """Generate enemy death sound - explosion-like."""
    import random

    samples = []
    duration = 0.2
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Noise with descending filter
        noise = random.uniform(-1.0, 1.0)
        # Low frequency rumble
        rumble = math.sin(2 * math.pi * 80 * t)
        value = noise * 0.6 + rumble * 0.4
        sample = int(value * 0.35 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.01, decay=0.15, sustain=0.1, release=0.05)
    save_wav("enemy_death.wav", samples)


def generate_shoot() -> None:
    """Generate shooting/firing sound."""
    import random

    samples = []
    duration = 0.1
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # High frequency burst with noise
        freq = 600 - (400 * t / duration)
        wave_val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        noise = random.uniform(-0.4, 0.4)
        value = wave_val * 0.5 + noise * 0.5
        sample = int(value * 0.3 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.005, decay=0.07, sustain=0.1, release=0.02)
    save_wav("shoot.wav", samples)


def generate_cannon() -> None:
    """Generate cannon fire sound - deep boom."""
    import random

    samples = []
    duration = 0.3
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Low frequency boom
        freq = 60
        rumble = math.sin(2 * math.pi * freq * t)
        noise = random.uniform(-0.8, 0.8)
        # Quick noise burst then rumble
        if t < 0.05:
            value = noise * 0.8 + rumble * 0.2
        else:
            value = noise * 0.2 + rumble * 0.6
        sample = int(value * 0.4 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.01, decay=0.15, sustain=0.3, release=0.1)
    save_wav("cannon.wav", samples)


def generate_door_unlock() -> None:
    """Generate door unlock sound."""
    samples = []
    duration = 0.25
    sample_rate = 44100

    # Two-note chime
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        if t < duration / 2:
            freq = 440  # A4
        else:
            freq = 554  # C#5
        value = math.sin(2 * math.pi * freq * t)
        sample = int(value * 0.3 * 32767)
        samples.append(sample)

    samples = apply_envelope(samples, attack=0.01, decay=0.1, sustain=0.5, release=0.1)
    save_wav("door_unlock.wav", samples)


def generate_menu_select() -> None:
    """Generate menu selection sound."""
    samples = []
    duration = 0.08
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = 600
        value = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        sample = int(value * 0.2 * 32767)
        samples.append(sample)

    samples = apply_envelope(samples, attack=0.005, decay=0.05, sustain=0.3, release=0.02)
    save_wav("menu_select.wav", samples)


def generate_menu_confirm() -> None:
    """Generate menu confirm sound."""
    samples = []
    duration = 0.15
    sample_rate = 44100

    # Two quick ascending notes
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        if t < duration / 2:
            freq = 523  # C5
        else:
            freq = 784  # G5
        value = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        sample = int(value * 0.25 * 32767)
        samples.append(sample)

    samples = apply_envelope(samples, attack=0.01, decay=0.05, sustain=0.5, release=0.05)
    save_wav("menu_confirm.wav", samples)


def generate_parrot_attack() -> None:
    """Generate parrot attack squawk."""
    import random

    samples = []
    duration = 0.12
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # High-pitched warble
        freq = 1200 + 200 * math.sin(2 * math.pi * 20 * t)
        value = math.sin(2 * math.pi * freq * t)
        noise = random.uniform(-0.2, 0.2)
        value = value * 0.7 + noise
        sample = int(value * 0.2 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.01, decay=0.06, sustain=0.3, release=0.04)
    save_wav("parrot_attack.wav", samples)


def generate_shield_hit() -> None:
    """Generate shield blocking sound."""
    import random

    samples = []
    duration = 0.15
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Metallic ping
        freq = 800
        freq2 = 1200
        val1 = math.sin(2 * math.pi * freq * t)
        val2 = math.sin(2 * math.pi * freq2 * t)
        noise = random.uniform(-0.2, 0.2)
        value = val1 * 0.4 + val2 * 0.3 + noise
        sample = int(value * 0.3 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.005, decay=0.1, sustain=0.2, release=0.04)
    save_wav("shield_hit.wav", samples)


def generate_boss_hit() -> None:
    """Generate boss taking damage sound."""
    import random

    samples = []
    duration = 0.2
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Heavy impact
        freq = 120
        rumble = math.sin(2 * math.pi * freq * t)
        freq2 = 200
        hit = 1.0 if math.sin(2 * math.pi * freq2 * t) >= 0 else -1.0
        noise = random.uniform(-0.3, 0.3)
        value = rumble * 0.4 + hit * 0.3 + noise
        sample = int(value * 0.35 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.01, decay=0.12, sustain=0.2, release=0.06)
    save_wav("boss_hit.wav", samples)


def generate_boss_death() -> None:
    """Generate boss death explosion sound."""
    import random

    samples = []
    duration = 0.8
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Multiple explosions
        freq = 50 + 30 * math.sin(2 * math.pi * 5 * t)
        rumble = math.sin(2 * math.pi * freq * t)
        noise = random.uniform(-1.0, 1.0)
        value = rumble * 0.5 + noise * 0.5
        sample = int(value * 0.4 * 32767)
        samples.append(max(-32768, min(32767, sample)))

    samples = apply_envelope(samples, attack=0.02, decay=0.3, sustain=0.3, release=0.3)
    save_wav("boss_death.wav", samples)


def generate_level_complete() -> None:
    """Generate level complete fanfare."""
    samples = []
    sample_rate = 44100

    # Simple victory melody: C-E-G-C (ascending)
    notes = [
        (523, 0.15),   # C5
        (659, 0.15),   # E5
        (784, 0.15),   # G5
        (1047, 0.3),   # C6 (held longer)
    ]

    for freq, dur in notes:
        note_samples = generate_wave(freq, dur, sample_rate, "square", 0.25)
        note_samples = apply_envelope(note_samples, attack=0.01, decay=0.05,
                                      sustain=0.7, release=0.05, sample_rate=sample_rate)
        samples.extend(note_samples)

    save_wav("level_complete.wav", samples)


def generate_game_over() -> None:
    """Generate game over sound - sad descending."""
    samples = []
    sample_rate = 44100

    # Descending minor notes
    notes = [
        (392, 0.25),   # G4
        (349, 0.25),   # F4
        (330, 0.25),   # E4
        (294, 0.4),    # D4
    ]

    for freq, dur in notes:
        note_samples = generate_wave(freq, dur, sample_rate, "square", 0.25)
        note_samples = apply_envelope(note_samples, attack=0.02, decay=0.1,
                                      sustain=0.5, release=0.1, sample_rate=sample_rate)
        samples.extend(note_samples)

    save_wav("game_over.wav", samples)


def generate_health_restore() -> None:
    """Generate health restore sound."""
    samples = []
    duration = 0.2
    sample_rate = 44100

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        # Gentle rising tone
        freq = 500 + (300 * t / duration)
        value = math.sin(2 * math.pi * freq * t)
        sample = int(value * 0.25 * 32767)
        samples.append(sample)

    samples = apply_envelope(samples, attack=0.02, decay=0.08, sustain=0.5, release=0.08)
    save_wav("health.wav", samples)


def generate_extra_life() -> None:
    """Generate extra life sound - triumphant."""
    samples = []
    sample_rate = 44100

    # Quick ascending fanfare
    notes = [
        (523, 0.1),    # C5
        (659, 0.1),    # E5
        (784, 0.1),    # G5
        (1047, 0.15),  # C6
        (1319, 0.2),   # E6
    ]

    for freq, dur in notes:
        note_samples = generate_wave(freq, dur, sample_rate, "square", 0.25)
        note_samples = apply_envelope(note_samples, attack=0.01, decay=0.03,
                                      sustain=0.7, release=0.03, sample_rate=sample_rate)
        samples.extend(note_samples)

    save_wav("extra_life.wav", samples)


def main():
    """Generate all sound effects."""
    print("Generating 8-bit sound effects...")
    ensure_output_dir()

    # Player sounds
    generate_jump()
    generate_land()
    generate_slash()
    generate_hit()
    generate_hurt()
    generate_death()

    # Collectible sounds
    generate_coin()
    generate_treasure()
    generate_powerup()
    generate_health_restore()
    generate_extra_life()

    # Combat sounds
    generate_enemy_death()
    generate_shoot()
    generate_cannon()
    generate_parrot_attack()
    generate_shield_hit()
    generate_boss_hit()
    generate_boss_death()

    # UI sounds
    generate_door_unlock()
    generate_menu_select()
    generate_menu_confirm()
    generate_level_complete()
    generate_game_over()

    print(f"\nGenerated {len(os.listdir(OUTPUT_DIR))} sound files in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
