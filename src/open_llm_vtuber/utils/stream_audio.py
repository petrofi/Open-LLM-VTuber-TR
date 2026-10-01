import base64
import io
from pydub import AudioSegment
from pydub.utils import make_chunks
from ..agent.output_types import Actions
from ..agent.output_types import DisplayText


def _get_volume_by_chunks(audio: AudioSegment, chunk_length_ms: int) -> list:
    """
    Calculate the normalized volume (RMS) for each chunk of the audio.

    Parameters:
        audio (AudioSegment): The audio segment to process.
        chunk_length_ms (int): The length of each audio chunk in milliseconds.

    Returns:
        list: Normalized volumes for each chunk.
    """
    chunks = make_chunks(audio, chunk_length_ms)
    volumes = [chunk.rms for chunk in chunks]
    max_volume = max(volumes)
    if max_volume == 0:
        raise ValueError("Audio is empty or all zero.")
    return [volume / max_volume for volume in volumes]


def prepare_audio_payload(
    audio_path: str | None,
    chunk_length_ms: int = 20,
    display_text: DisplayText = None,
    actions: Actions = None,
    forwarded: bool = False,
) -> dict[str, any]:
    """
    Prepares the audio payload for sending to a broadcast endpoint.
    If audio_path is None, returns a payload with audio=None for silent display.

    Parameters:
        audio_path (str | None): The path to the audio file to be processed, or None for silent display
        chunk_length_ms (int): The length of each audio chunk in milliseconds
        display_text (DisplayText, optional): Text to be displayed with the audio
        actions (Actions, optional): Actions associated with the audio

    Returns:
        dict: The audio payload to be sent
    """
    if isinstance(display_text, DisplayText):
        display_text = display_text.to_dict()

    if not audio_path:
        # Return payload for silent display
        return {
            "type": "audio",
            "audio": None,
            "volumes": [],
            "slice_length": chunk_length_ms,
            "display_text": display_text,
            "actions": actions.to_dict() if actions else None,
            "forwarded": forwarded,
        }

    try:
        # PyAV ships the decoder libraries used by Faster-Whisper. This avoids
        # requiring a separate system-wide FFmpeg executable in the installer.
        if str(audio_path).lower().endswith(".wav"):
            with open(audio_path, "rb") as source:
                audio = AudioSegment.from_file(source, format="wav")
        else:
            import av

            pcm = io.BytesIO()
            resampler = av.AudioResampler(format="s16", layout="mono", rate=24000)
            with av.open(audio_path) as container:
                for frame in container.decode(audio=0):
                    for converted in resampler.resample(frame):
                        pcm.write(converted.to_ndarray().tobytes())
                for converted in resampler.resample(None):
                    pcm.write(converted.to_ndarray().tobytes())
            audio = AudioSegment(pcm.getvalue(), sample_width=2, frame_rate=24000, channels=1)
        with audio.export(format="wav") as exported:
            audio_bytes = exported.read()
    except Exception as e:
        raise ValueError(
            f"Error loading or converting generated audio file to wav file '{audio_path}': {e}"
        )
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    volumes = _get_volume_by_chunks(audio, chunk_length_ms)

    payload = {
        "type": "audio",
        "audio": audio_base64,
        "volumes": volumes,
        "slice_length": chunk_length_ms,
        "display_text": display_text,
        "actions": actions.to_dict() if actions else None,
        "forwarded": forwarded,
    }

    return payload


# Example usage:
# payload, duration = prepare_audio_payload("path/to/audio.mp3", display_text="Hello", expression_list=[0,1,2])
