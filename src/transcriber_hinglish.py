# !pip install transformers torch soundfile accelerate
import torch
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from transformers import pipeline
import os

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

pipe = pipeline(
    "automatic-speech-recognition",
    model="Trelis/whisper-hinglish-preview",
    generate_kwargs={"language": "hi", "num_beams": 1},
    dtype=torch.float16,
    device=0 if device == "cuda" else -1,
)

audio_path = "samples/video_audio.wav"
chunk_length_ms = 10_000  # 10 seconds

audio = AudioSegment.from_wav(audio_path).set_frame_rate(16000).set_channels(1)


# --- VAD step: find the actual speech regions (skip silence) ---
speech_ranges_ms = detect_nonsilent(
    audio,
    min_silence_len=300,
    silence_thresh=audio.dBFS - 20,
)
# Drop obviously-too-short OR too-quiet blips (likely breath/noise, not real speech)
speech_ranges_ms = [
    (s, e) for s, e in speech_ranges_ms
    if (e - s) >= 200 and audio[s:e].dBFS > (audio.dBFS - 10)
]
# --- Safeguards: merge/split so chunks aren't too short or too long ---
MIN_CHUNK_MS = 1500
MAX_CHUNK_MS = 5000
def apply_safeguards(ranges):
    merged = []
    for start, end in ranges:
        if merged and (start - merged[-1][1]) < 300 and (end - merged[-1][0]) < MAX_CHUNK_MS:
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))

    final = []
    for start, end in merged:
        length = end - start
        if length > MAX_CHUNK_MS:
            pos = start
            while pos < end:
                piece_end = min(pos + MAX_CHUNK_MS, end)
                final.append((pos, piece_end))
                pos = piece_end
        elif length < MIN_CHUNK_MS:
            pad = (MIN_CHUNK_MS - length) // 2
            final.append((max(0, start - pad), min(len(audio), end + pad)))
        else:
            final.append((start, end))
    return final

speech_ranges_ms = apply_safeguards(speech_ranges_ms)

print(f"Detected {len(speech_ranges_ms)} speech segments (after safeguards)")

# --- Transcribe each real speech segment ---
os.makedirs("chunks", exist_ok=True)

segments = []
for idx, (start_ms, end_ms) in enumerate(speech_ranges_ms):
    chunk = audio[start_ms:end_ms]

    chunk_path = f"chunks/chunk_{idx}.wav"
    chunk.export(chunk_path, format="wav")

    result = pipe(chunk_path)
    text = result["text"].strip()

    if text:
        segments.append({
            "start": start_ms / 1000.0,
            "end": end_ms / 1000.0,
            "text": text
        })

for seg in segments:
    print(f"[{seg['start']:.2f} -> {seg['end']:.2f}] {seg['text']}")