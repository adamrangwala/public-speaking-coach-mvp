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

def submit_for_transcription(file_url: str, webhook_url: str) -> str:
    """
    Submits a file to AssemblyAI for transcription and returns the transcript ID.
    """
    transcriber = get_transcriber()
    if not transcriber:
        raise ConnectionError("AssemblyAI client is not available or configured.")

    config = aai.TranscriptionConfig(
        webhook_url=webhook_url,
        punctuate=True,
        format_text=True
    )
    
    transcript = transcriber.submit(file_url, config=config)
    
    return transcript.id