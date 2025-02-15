import streamlit as st
import assemblyai as aai
from dotenv import load_dotenv
import os

load_dotenv()

# AssemblyAI API key
aai.settings.api_key = os.getenv("api_key")

# UI Title
st.title("Video to Text Transcription")
st.write("Upload a video file and choose a language to transcribe the speech. Speaker detection is enabled.")

# Initialize session state for transcription text
if "transcription_text" not in st.session_state:
    st.session_state.transcription_text = ""

# File uploader
uploaded_file = st.file_uploader("Upload a video file here:", type=["mp4", "mov", "avi", "mkv"])

# Clear transcription when a new file is uploaded
if uploaded_file:
    if "last_uploaded_file" in st.session_state and uploaded_file.name != st.session_state.last_uploaded_file:
        st.session_state.transcription_text = ""  # Reset transcript for a new file

    st.session_state.last_uploaded_file = uploaded_file.name  # Store current file name

    # Define language options
    language_options = {"Russian (RU)": "ru", "English (EN)": "en", "Lithuanian (LT)": "lt"}
    language_placeholder = "Choose a language"
    languages_list = [language_placeholder] + list(language_options.keys())

    # Dropdown for language selection
    selected_language = st.selectbox("Select language:", options=languages_list)

    # Check if a valid language has been selected
    if selected_language == language_placeholder:
        st.info("Please select a language to proceed.")
    else:
        # Only allow processing when a valid language is selected
        if st.button("🚀 Start Processing"):
            try:
                # Retrieve the language code
                language_code = language_options[selected_language]

                # Configure transcription settings
                config = aai.TranscriptionConfig(
                    language_code=language_code,
                    speaker_labels=True,  # Enable speaker diarization
                    speech_model=aai.SpeechModel.best  # Lightweight model
                )

                # Process the video file using a spinner for feedback
                with st.spinner("⏳ Processing video... This might take a few minutes."):
                    transcriber = aai.Transcriber()
                    transcript = transcriber.transcribe(uploaded_file, config)

                # Check for transcription errors
                if transcript.error:
                    st.error(f"🚨 Error: {transcript.error}")
                else:
                    # st.success("✅ Transcription completed!")

                    # Format transcription output
                    transcription_text = ""
                    for utterance in transcript.utterances:
                        transcription_text += f"Speaker {utterance.speaker}: {utterance.text}\n"

                    # Store transcription in session state (overwrite previous)
                    st.session_state.transcription_text = transcription_text

            except Exception as e:
                st.error(f"🚨 An unexpected error occurred: {str(e)}")

# Keep the transcription result visible until the user removes the video
if uploaded_file and st.session_state.transcription_text:
    st.subheader("Transcription Output:")
    st.text_area("Transcript:", value=st.session_state.transcription_text, height=300, key="transcript_display")

    # Download button (does not reset UI)
    st.download_button(
        label="📥 Download as TXT",
        data=st.session_state.transcription_text,
        file_name="transcription.txt",
        mime="text/plain"
    )
