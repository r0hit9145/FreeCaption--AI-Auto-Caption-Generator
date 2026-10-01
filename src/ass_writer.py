import os
import re


MIN_WORD_DURATION = 0.15  # seconds — avoid flashing words with ~0 duration


def format_ass_timestamp(seconds: float) -> str:
    """
    Converts seconds into .ass timestamp format: H:MM:SS.cc (centiseconds)
    e.g. 75.5 -> '0:01:15.50'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))

    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def write_ass(words: list, output_path: str,
              font_name: str = "Noto Sans Devanagari",
              font_size: int = 50,
              text_color: str = "&H00FFFFFF",
              highlight_color: str = "&H00FFFFFF",
              color_palette: list = None,
              box_background: bool = False,
              fire: bool = False,
              uppercase: bool= False,
              italic: bool = False,
              glow: bool = False,
              pop_animation: bool = False) -> str:
    """
    Writes word-level timestamps into a styled .ass subtitle file,
    displaying ONE word at a time (word-by-word animated captions).

    Args:
        words: List of dicts shaped like [{"start": 0.5, "end": 0.8, "text": "hi"}, ...]
               (the exact output of transcriber.py's transcribe_words())
        output_path: Where to save the .ass file.
        font_name: Font used for rendering (must be installed on the system).
        font_size: Font size in points.
        text_color: Default text color, in &HAABBGGRR hex format (ASS color format).
        highlight_color: Color used for the active/popped word (currently same
                          styling applied to every word, since only one shows at a time).

    Returns:
        Path to the written .ass file.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # BorderStyle 3 = opaque box behind text; BorderStyle 1 = outline only
    border_style = 3 if box_background else 1
    back_color = "&H00000000" if box_background else "&H00000000"

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,{font_name},{font_size * 2},{highlight_color},{text_color},&H00000000,{back_color},-1,0,0,0,100,100,0,0,{border_style},4,0,2,50,50,450,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = []
    last_end = 0.0
    for idx, word in enumerate(words):
        start = word["start"]
        end = word["end"]

        text = word["text"].strip()
        if not text:
            continue

        # Keep only English alphabet characters (strips ,.-/\ and everything else)
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

        # Prevent overlap: this word can't start before the previous one finished
        if start < last_end:
            start = last_end

        # Guarantee a minimum visible duration so quick words don't flash invisibly
        if (end - start) < MIN_WORD_DURATION:
            end = start + MIN_WORD_DURATION

        # Safety: end must never fall before start after the adjustments above
        if end <= start:
            end = start + MIN_WORD_DURATION

        last_end = end
        
        start_ts = format_ass_timestamp(start)
        end_ts = format_ass_timestamp(end)
        override_tags = ""
        is_highlight = False

        if color_palette:
            word_color = color_palette[idx % len(color_palette)]
            override_tags += f"\\c{word_color}"
            is_highlight = (idx % len(color_palette)) == 1

        if italic:
            override_tags += "\\i1"

        if is_highlight:
            # --- Highlight word: TWO dialogue lines for the glow effect ---
            word_color = color_palette[idx % len(color_palette)]

            # Layer 0: blurred glow halo behind the text — softer, more subtle
            # Layer 0: blurred glow halo behind the text — much softer
            glow_tags = f"\\c{word_color}\\3c{word_color}\\bord0\\blur3\\1a&H90&\\3a&H90&\\fscx100\\fscy100\\t(0,120,\\fscx125\\fscy125)"
            if italic:
                glow_tags += "\\i1"
            glow_text = f"{{{glow_tags}}}{text}"
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Word,,0,0,0,,{glow_text}")

            # Layer 1: sharp text on top, same grow animation
            sharp_tags = f"\\c{word_color}\\bord2\\blur0\\fscx100\\fscy100\\t(0,120,\\fscx125\\fscy125)"
            if italic:
                sharp_tags += "\\i1"
            sharp_text = f"{{{sharp_tags}}}{text}"
            lines.append(f"Dialogue: 1,{start_ts},{end_ts},Word,,0,0,0,,{sharp_text}")

        else:
            # --- Normal (white) word: single line as before ---
            if pop_animation:
                override_tags += "\\fscx0\\fscy0\\t(0,150,\\fscx100\\fscy100)"

            if glow:
                override_tags += "\\3c&H00000000\\bord5\\blur0\\shad1"

            styled_text = f"{{{override_tags}}}{text}" if override_tags else text
            lines.append(f"Dialogue: 0,{start_ts},{end_ts},Word,,0,0,0,,{styled_text}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(lines))
        f.write("\n")

    return output_path


if __name__ == "__main__":
    # Small fake dataset to test formatting alone, same principle as subtitle_writer.py
    fake_words = [
        {"start": 0.5, "end": 0.8, "text": "Hello"},
        {"start": 0.8, "end": 1.0, "text": "world"},
        {"start": 1.0, "end": 1.0, "text": "this"},  # zero-duration test case
    ]

    # zeemo_palette = ["&H0000FFFF", "&H0000FF00", "&H00FF00FF", "&H0000A5FF"]  # yellow, green, pink, orange
    alt_palette = ["&H00FFFFFF", "&H0034FF39"]  # white, green — alternates by word index
    path = write_ass(fake_words,
        "output/word_captions.ass",
        color_palette=alt_palette,
        # box_background=True,
        # pop_animation=True
        )
    print(f"ASS file written to: {path}")