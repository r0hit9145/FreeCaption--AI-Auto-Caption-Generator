I built an automated caption generator for short-form videos — think YouTube Shorts or Reels — that transcribes speech and burns styled, word-by-word animated captions directly into the video.

The pipeline is: extract audio with ffmpeg, transcribe it using OpenAI's Whisper model (via faster-whisper) to get word-level timestamps, generate a styled .ass subtitle file, then burn that into the final video. I built two variants — a plain English pipeline, and a Hinglish (Hindi-English code-switched) version, which was the harder problem since Whisper is inconsistent about which script it transcribes mixed-language speech into.

A few specific challenges I solved: Whisper sometimes mis-transcribes domain-specific English words when they're spoken in a Hindi sentence, so I used initial_prompt biasing and a corrections dictionary to improve accuracy. I also built the caption styling manually at the .ass subtitle-format level — things like a scale-up 'pop' animation and a two-layer glow effect for highlighted words, since that's not something standard libraries give you out of the box.

Most recently, I built a Streamlit frontend on top of it — upload a video, review and manually correct the auto-generated transcript in an editable table before generating the final video, since transcription is never 100% accurate. I'm also handling session isolation for deployment, so multiple users hitting the app at once don't collide on shared files."



Known limitations / Backlog
- Hinglish captions currently use VAD + fixed max-chunk-length segmentation.
  For continuous speakers with few natural pauses, this can cause mid-sentence
  caption breaks. A proper fix requires word-level timestamps (segment by
  word/phrase groups instead of silence detection) — planned as a future upgrade.
  
- Heavy Hinglish model (Trelis/whisper-hinglish-preview) requires GPU;
  currently run via Google Colab, not integrated into the local pipeline.