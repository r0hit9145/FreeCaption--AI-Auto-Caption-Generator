"""
audio_extractor.py
 
Step 1 of the auto-caption pipeline.
Wraps ffmpeg to pull the audio track out of a video file and convert it
to the format Whisper expects: mono, 16kHz WAV.]
"""
import subprocess
import os

def extract_audio(video_path: str, output_path: str = None) -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if output_path is None:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(os.path.dirname(video_path), f"{base_name}_audio.wav")

    
    command = [
        "ffmpeg",
        "-y",              # overwrite output file if it already exists
        "-i", video_path,  # input file
        "-ar", "16000",    # sample rate: 16kHz (what Whisper expects)
        "-ac", "1",        # audio channels: mono
        output_path
    ]
    # capture_output hides ffmpeg's verbose logs unless something fails
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")

    print(f"Audio extracted successfully: {output_path}")
    return output_path



# Quick manual test — run this file directly to try it on a sample video
if __name__ == "__main__":
    test_video = "samples/video.mp4"
    extract_audio(test_video) 