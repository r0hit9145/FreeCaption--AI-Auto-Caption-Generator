from faster_whisper import WhisperModel


def transcribe(audio_path: str, model_size: str = "base") -> list:

    """
    Transcribes an audio file into text segments with timestamps,
    using Whisper. Forces English/Roman-script output so mixed
    Hindi-English (Hinglish) speech is transcribed in Latin script
    instead of Devanagari.

    Args:
        audio_path: Path to a .wav audio file (e.g. 'output/video_audio.wav')
        model_size: Whisper model size to load — 'tiny', 'base', 'small',
                    'medium', or 'large'. Bigger = more accurate but slower.

    Returns:
        A list of dicts shaped like:
        [{"start": 0.0, "end": 2.3, "text": "hello world"}, ...]
        — the exact shape write_srt() expects.
    """


    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    raw_segments, info = model.transcribe(
        audio_path,
        language="en",
        task="transcribe",
        word_timestamps=True,
    )
    segments = []
    for seg in raw_segments:
        for word in seg.words:
            segments.append({
                "start": word.start,
                "end": word.end,
                "text": word.text
            })
 
    return segments

def transcribe_words(audio_path: str, model_size: str = "base", language: str = None, initial_prompt: str = None) -> list:
    """
    Transcribes audio into individual WORD-level segments with timestamps,
    instead of sentence/phrase-level segments. Used for word-by-word
    animated captions (one word visible at a time, synced to speech).
 
    Args:
        Same as transcribe() above.
 
    Returns:
        A list of dicts shaped like:
        [{"start": 0.52, "end": 0.81, "text": "hello"}, ...]
        — one entry per spoken word, not per sentence.
    """
 
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=4)
 
    raw_segments, info = model.transcribe(
        audio_path,
        language="en",
        task="transcribe",
        vad_filter=True,
        condition_on_previous_text=True,
        beam_size=5,
        initial_prompt=initial_prompt,
        word_timestamps=True
    )
    print(f"Language used: {language if language else f'auto-detected as {info.language}'}")
 
    words = []
    for seg in raw_segments:
        for word in seg.words:
            words.append({
                "start": word.start,
                "end": word.end,
                "text": word.word.strip()
            })
 
    return words

if __name__ == "__main__":
    # result = transcribe("samples/video_audio.wav")
    # for seg in result:
    #     print(f"[{seg['start']:.2f} -> {seg['end']:.2f}] {seg['text']}")
    result = transcribe_words("samples/video_audio.wav")
 
    for word in result:
        print(f"[{word['start']:.2f} -> {word['end']:.2f}] {word['text']}")