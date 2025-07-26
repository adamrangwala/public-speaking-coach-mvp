import os
import ffmpeg
import tempfile

HLS_PLAYLIST_DIR = "hls_playlists"
PROCESSED_VIDEOS_DIR = "processed_videos"

def preprocess_video(input_path: str, video_id: int):
    """
    Standardizes a video to H.264/MP4, 720p, 30fps with two-pass encoding.
    """
    os.makedirs(PROCESSED_VIDEOS_DIR, exist_ok=True)
    output_filename = f"{video_id}.mp4"
    output_path = os.path.join(PROCESSED_VIDEOS_DIR, output_filename)
    
    pass_log_prefix = os.path.join(tempfile.gettempdir(), f"{video_id}_pass_log")

    try:
        # Probe video to check if it needs resizing/fps change
        probe = ffmpeg.probe(input_path)
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        width = video_stream['width']
        height = video_stream['height']
        fps = eval(video_stream['r_frame_rate'])

        vf_filters = []
        if height > 720:
            vf_filters.append('scale=-2:720')
        if fps > 30:
            vf_filters.append('fps=30')
        
        vf_filter_str = ",".join(vf_filters) if vf_filters else "null"

        # Two-pass encoding
        # Pass 1
        (
            ffmpeg
            .input(input_path)
            .output(
                'pipe:', # Discard output
                format='null',
                vcodec='libx264',
                vf=vf_filter_str,
                pass_log=pass_log_prefix,
                pass_=1,
                an=None # Ignore audio for the first pass
            )
            .run(capture_stdout=True, capture_stderr=True)
        )

        # Pass 2
        (
            ffmpeg
            .input(input_path)
            .output(
                output_path,
                vcodec='libx264',
                vf=vf_filter_str,
                pass_log=pass_log_prefix,
                pass_=2,
                acodec='aac',
                audio_bitrate='128k',
                map_metadata=-1, # Strip metadata
                **{'preset': 'medium', 'crf': 23}
            )
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print('FFmpeg Error:', e.stderr.decode())
        raise e
    finally:
        # Clean up pass log files
        for f in [f"{pass_log_prefix}-0.log", f"{pass_log_prefix}-0.log.mbtree"]:
            if os.path.exists(f):
                os.remove(f)

    return output_path

def transcode_to_hls(input_path: str, video_id: int):
    """
    Transcodes a preprocessed video file to HLS format.
    """
    output_dir = os.path.join(HLS_PLAYLIST_DIR, str(video_id))
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "playlist.m3u8")

    try:
        (
            ffmpeg
            .input(input_path)
            .output(
                output_file,
                format='hls',
                hls_time=10,
                hls_list_size=0,
                hls_segment_filename=os.path.join(output_dir, 'segment%03d.ts'),
                vcodec='copy', # Use the already encoded video stream
                acodec='copy'  # Use the already encoded audio stream
            )
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print('FFmpeg Error during HLS transcoding:', e.stderr.decode())
        raise e

    return f"/{output_dir}/playlist.m3u8".replace("\\", "/")