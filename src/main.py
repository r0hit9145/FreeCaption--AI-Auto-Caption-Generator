#let's connect with me study with me
import argparse
import os
from audio_extractor import extract_audio
from subtitle_writer import write_srt
from transcriber import transcribe
from caption_burner import burn_captions


def run_pipeline(
    video_path: str,
    samples_dir: str,
    output_dir: str,
    output_path: str = None,
    model_size: str = "base",
    language: str = None,
) -> str:
    """
    Runs the full auto-caption pipeline end to end:
    video -> audio -> transcript -> srt -> captioned video

    Args:
        video_path: Path to the input video file.
        samples_dir: Directory for intermediate files (e.g. extracted audio).
        output_dir: Directory for final output files (srt, captioned video).
        output_path: Path for the final captioned video. Auto-generated if not given.
        model_size: Whisper model size to use for transcription.
        language: Force spoken language, e.g. 'en' or 'hi'. Default: auto-detect.

    Returns:
        Path to the final captioned video.
    """

    os.makedirs(samples_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    print(f"[1/4] Extracting audio from: {video_path}")
    audio_path = extract_audio(video_path, samples_dir)
    print(f"      -> {audio_path}")

    print(f"[2/4] Transcribing audio (model: {model_size})...")
    segments = transcribe(audio_path, model_size=model_size, language=language)
    print(f"      -> {len(segments)} segments transcribed")

    print("[3/4] Writing subtitle file...")
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    write_srt(segments, srt_path)
    print(f"      -> {srt_path}")

    print("[4/4] Burning captions onto video...")
    if output_path is None:
        output_path = os.path.join(output_dir, f"{base_name}_captioned.mp4")
    final_path = burn_captions(video_path, srt_path, output_path)
    print(f"      -> {final_path}")

    return final_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate burned-in captions for a video using Whisper."
    )
    parser.add_argument("--input", required=True, help="Path to input video file")
    parser.add_argument("--samples-dir", required=False, default="samples", help="Directory for intermediate files")

    parser.add_argument("--output-dir", required=False, default="output", help="Directory for output files")
    parser.add_argument("--output", required=False, default=None, help="Path for output captioned video")
    parser.add_argument("--model", required=False, default="base", help="Whisper model size (tiny/base/small/medium/large)")
    parser.add_argument("--language", required=False, default=None, help="Force spoken language, e.g. 'en' or 'hi'. Default: auto-detect")
    args = parser.parse_args()

    result_path = run_pipeline(
        args.input,
        args.samples_dir,
        args.output_dir,
        args.output,
        args.model,
        args.language,
    )
    print(f"\nDone. Captioned video: {result_path}")