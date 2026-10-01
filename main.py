import streamlit as st
import os
import time
import uuid
import shutil
import sys


# Make src/ modules importable directly (instead of running scripts as subprocesses),
# since editing needs to happen BETWEEN transcription and video generation.
sys.path.insert(0, "src")

from audio_extractor import extract_audio
from transcriber import transcribe_words
from ass_writer import write_ass
from caption_burner import burn_captions

st.set_page_config(page_title="Auto Captions", layout="centered")
st.title("🎬 FreeCaption")
st.write("Upload a video, review the transcript, fix any wrong words, then generate captions.")

# --- Cleanup helper (NEW) ---
CLEANUP_MAX_AGE_MINUTES = 2  # short for testing — bump up once you're done
def cleanup_stale_sessions(base_dir, max_age_hours= CLEANUP_MAX_AGE_MINUTES):
    if not os.path.isdir(base_dir):
        return
    now = time.time()
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if os.path.isdir(path) and (now - os.path.getmtime(path)) > max_age_hours * 60:
            shutil.rmtree(path, ignore_errors=True)
# --- end cleanup helper ---


# --- Per-session identity and folders (NEW) ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

session_id = st.session_state.session_id
samples_dir = os.path.join("samples", session_id)
output_dir = os.path.join("output", session_id)
os.makedirs(samples_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

cleanup_stale_sessions("samples")   # NEW — runs once per script run
cleanup_stale_sessions("output")    # NEW
# --- end new block ---

if "words" not in st.session_state:
    st.session_state.words = None

if "input_path" not in st.session_state:
    st.session_state.input_path = None

uploaded_file = st.file_uploader("Upload your video (.mp4)", type=["mp4"])

if uploaded_file is not None:
    input_path = os.path.join(samples_dir, uploaded_file.name)   # changed
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.input_path = input_path
    st.video(input_path)

    if st.button("1. Transcribe"):
        with st.spinner("Transcribing audio... this can take a minute."):
            audio_path = extract_audio(input_path)
            words = transcribe_words(audio_path, model_size="base")
            st.session_state.words = words
        st.success(f"Transcribed {len(st.session_state.words)} words. Review and edit below.")

if st.session_state.words:
    st.subheader("2. Review & edit transcript")
    st.caption("Edit the 'text' column to fix any wrong words. Timestamps are locked to avoid breaking sync.")

    edited_words = st.data_editor(
        st.session_state.words,
        column_config={
            "start": st.column_config.NumberColumn("Start (s)", format="%.2f", disabled=True),
            "end": st.column_config.NumberColumn("End (s)", format="%.2f", disabled=True),
            "text": st.column_config.TextColumn("Word"),
        },
        num_rows="fixed",
        use_container_width=True,

        key="word_editor",
    )

    st.subheader("3. Generate")
    if st.button("Generate Captioned Video"):
        with st.spinner("Writing captions and burning into video..."):
            base_name = os.path.splitext(os.path.basename(st.session_state.input_path))[0]
            ass_path = os.path.join(output_dir, f"{base_name}_words.ass")   # changed

            white_green_palette = ["&H00FFFFFF", "&H0000FF00"]
            write_ass(
                edited_words,
                ass_path,
                uppercase=True,
                glow=True,
                italic=True,
                pop_animation = True,
                color_palette=white_green_palette,
            )

            final_path = burn_captions(st.session_state.input_path, ass_path, None)

        st.success("Captions generated!")
        st.video(final_path)
        with open(final_path, "rb") as f:
            st.download_button(
                "Download captioned video",
                f,
                file_name=os.path.basename(final_path),
            )