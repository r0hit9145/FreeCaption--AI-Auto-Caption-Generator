import subprocess
import os


def burn_captions(video_path: str, srt_path: str, output_path: str = None) -> str:
    """
    Burns (permanently overlays) subtitles from an .srt file onto a video,
    producing a new video file with visible captions baked into the frames.
 
    Args:
        video_path: Path to the original input video.
        srt_path: Path to the .srt subtitle file to overlay.
        output_path: Where to save the captioned video. Auto-generated if not given.
 
    Returns:
        The path to the final captioned video file.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"Subtitle file not found: {srt_path}")

    if output_path is None:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join("output", f"{base_name}_captioned.mp4")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # ffmpeg's subtitles filter needs a path it can read cleanly —
    # wrapping in quotes protects against spaces or special characters.
    srt_path_escaped = srt_path.replace("\\", "/")
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", f"subtitles={srt_path_escaped}",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "0:a:0",
        output_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")

    return output_path


if __name__ == "__main__":
    output = burn_captions("samples/day_14_without_caption.mp4", "output/day_14_without_caption_words.ass")
    print(f"Captioned video saved to: {output}")