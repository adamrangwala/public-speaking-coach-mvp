import assemblyai as aai
from decouple import config

ASSEMBLYAI_API_KEY = config("ASSEMBLYAI_API_KEY", default=None)

def is_transcription_configured():
    """Check if the AssemblyAI API key is set."""
    return ASSEMBLYAI_API_KEY is not None

def get_transcriber():
    """Initialize and return an AssemblyAI transcriber."""
    if not is_transcription_configured():
        return None
    aai.settings.api_key = ASSEMBLYAI_API_KEY
    return aai.Transcriber()

def transcribe_and_poll(file_url: str) -> str:
    """
    Transcribes a file from a URL using AssemblyAI and polls for the result.
    Returns the transcript text.
    """
    transcriber = get_transcriber()
    if not transcriber:
        raise ConnectionError("AssemblyAI client is not available or configured.")

    config = aai.TranscriptionConfig(
        punctuate=True,
        format_text=True,
        speech_model=aai.SpeechModel.best,
        disfluences=True
    )

    transcript = transcriber.transcribe(file_url, config=config)

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"Transcription failed: {transcript.error}")

    return transcript.text