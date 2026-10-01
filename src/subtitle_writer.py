import os

def format_timestamp(seconds: float) -> str:
    """
    Converts a time in seconds (e.g. 75.5) into SRT timestamp format:
    HH:MM:SS,mmm  (e.g. '00:01:15,500')
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
 
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def write_srt(segments: list, output_path: str) -> str:
    """
    Writes a list of caption segments into a valid .srt subtitle file.
 
    Args:
        segments: A list of dicts, each shaped like:
                  {"start": 0.0, "end": 2.5, "text": "hello world"}
        output_path: Where to save the .srt file (e.g. 'output/captions.srt')
 
    Returns:
        The path to the written .srt file.
    """
 
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
 
    with open(output_path, "w", encoding="utf-8") as f:
        for index, segment in enumerate(segments, start=1):
            start_ts = format_timestamp(segment["start"])
            end_ts = format_timestamp(segment["end"])
            text = segment["text"].strip()
 
            f.write(f"{index}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{text}\n")
            f.write("\n")
 
    return output_path


if __name__ == "__main__":
    # Fake/dummy data — standing in for real Whisper output for now.
    # This lets us test the SRT formatting logic completely on its own.
    fake_segments = [
        {"start": 0.0, "end": 2.0, "text": "     Hello, this is a test caption."},
        {"start": 2.0, "end": 4.5, "text": "    Yeh dusra caption hai."},
        {"start": 4.5, "end": 7.0, "text": "    Auto caption tool is working.      "},
    ]
 
    srt_path = write_srt(fake_segments, "output/captions.srt")
    print(f"SRT file written to: {srt_path}")