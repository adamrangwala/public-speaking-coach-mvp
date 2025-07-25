import os
import ffmpeg

HLS_PLAYLIST_DIR = "hls_playlists"

def transcode_to_hls(input_url: str, video_id: int):
    """
    Transcodes a video from a URL to HLS format.

    Args:
        input_url: The URL of the input video file.
        video_id: The ID of the video, used for the output directory.
    """
    output_dir = os.path.join(HLS_PLAYLIST_DIR, str(video_id))
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "playlist.m3u8")

    try:
        (
            ffmpeg
            .input(input_url)
            .output(
                output_file,
                format='hls',
                hls_time=10,
                hls_list_size=0,
                hls_segment_filename=os.path.join(output_dir, 'segment%03d.ts'),
                vcodec='libx264',
                acodec='aac',
                ar=48000, # Audio sample rate
                ac=2, # Stereo audio
                audio_bitrate='128k', # Audio bitrate
                vf='format=yuv420p' # Set pixel format for broad compatibility
            )
            .run(capture_stdout=True, capture_stderr=True)
        )
    except Exception as e:
        print(f"Error during transcoding: {e}")
        raise e

    return f"/{output_dir}/playlist.m3u8".replace("\\", "/")