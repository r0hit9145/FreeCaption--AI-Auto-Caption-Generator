import argparse
import os
from audio_extractor import extract_audio
from transcriber import transcribe_words
from ass_writer import write_ass
from caption_burner import burn_captions



def run_word_caption_pipeline(video_path: str, output_path: str = None, model_size: str = "base", language: str = None) -> str:
    """
    Runs the word-by-word animated caption pipeline end to end:
    video -> audio -> word-level transcript -> .ass file -> captioned video
 
    Args:
        video_path: Path to the input video file.
        output_path: Path for the final captioned video. Auto-generated if not given.
        model_size: Whisper model size to use for transcription.
        language: Force a spoken language (e.g. 'en', 'hi'). None = auto-detect.
 
    Returns:
        Path to the final captioned video.
    """
    print(f"[1/4] Extracting audio from: {video_path}")
    audio_path = extract_audio(video_path)
    print(f"      -> {audio_path}")

    print(f"[2/4] Transcribing word-level timestamps (model: {model_size})...")
    words = transcribe_words(audio_path, model_size=model_size, language=language)
    print(f"      -> {len(words)} words transcribed")

    print("[3/4] Writing .ass subtitle file...")
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    ass_path = os.path.join("output", f"{base_name}_words.ass")
    # zeemo_palette = ["&H0000FFFF", "&H0000FF00", "&H00FF00FF", "&H0000A5FF"]  # yellow, green, pink, orange
    white_green_palette = ["&H00FFFFFF", "&H0000FF00"]  # white, green, alternating
    write_ass(words, ass_path, uppercase=True, glow = True, italic=True, pop_animation= True, color_palette= white_green_palette)
    print(f"      -> {ass_path}")


    print("[4/4] Burning word-by-word captions onto video...")
    final_path = burn_captions(video_path, ass_path, output_path)
    print(f"      -> {final_path}")
 
    return final_path


#this is our main funtion to call each module...
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate word-by-word animated captions for a video."
    )
    parser.add_argument("--input", required=True, help="Path to input video file")
    parser.add_argument("--output", required=False, default=None, help="Path for output captioned video")
    parser.add_argument("--model", required=False, default="base", help="Whisper model size (tiny/base/small/medium/large)")
    parser.add_argument("--language", required=False, default=None, help="Force spoken language, e.g. 'en' or 'hi'. Default: auto-detect")
    args = parser.parse_args()
    result_path = run_word_caption_pipeline(args.input, args.output, args.model, args.language)
    print(f"\nDone. Word-captioned video: {result_path}")