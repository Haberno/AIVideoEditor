from faster_whisper import WhisperModel
import subprocess
import os


def create_directories(base_path, video_file_name):
    # Create base directory from the video file name
    file_name = os.path.splitext(video_file_name)[0]

    base_dir = os.path.join(base_path, file_name)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Create subdirectories for text and images
    text_dir = os.path.join(base_dir, f"text")
    image_dir = os.path.join(base_dir, f"images")
    match_dir = os.path.join(base_dir, f"matches")
    clips_dir = os.path.join(base_dir, f"clips")
    os.makedirs(text_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(match_dir, exist_ok=True)
    os.makedirs(clips_dir, exist_ok=True)
    
    text_dir = os.path.join(text_dir, f"{video_file_name}.txt")

    return text_dir, image_dir


model_size = "large-v3"
model = WhisperModel(model_size, device="cuda", compute_type="float16")

def extract_images_at_intervals(video_file, image_output_path, interval):
    # Get the total duration of the video
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    duration = float(result.stdout)
    
    # Calculate the maximum number of frames based on the interval
    max_frames = int(duration / interval)
    
    # Prepare the command to extract frames
    command = [
        "ffmpeg",
        "-hwaccel", "cuda",  # Use GPU acceleration if available
        "-i", video_file,
        "-frames:v", str(max_frames),
        "-vf", f"fps=1/{interval}",
        "-q:v", "2",  # Quality of the output frames
        f"{image_output_path}/frame_%05d.jpg"
    ]
    
    # Run the command to extract frames
    subprocess.run(command, check=True)

    # Rename files to reflect the interval timestamps
    for i in range(max_frames):
        os.rename(
            os.path.join(image_output_path, f"frame_{str(i+1).zfill(5)}.jpg"),
            os.path.join(image_output_path, f"frame_{i * interval:.1f}.jpg")
        )


input_video_path = "inputs/anime_episode.mp4"
input_audio_path = "inputs/summary.mp3"
base_path = "output"
interval = 2

text_output_path, image_output_path = create_directories(base_path, os.path.basename(input_video_path))

extract_images_at_intervals(input_video_path, image_output_path, interval)
    


def transcribe_audio(model, audio_file, text_output_path) :
    segments, info = model.transcribe(audio_file, beam_size=5, language="en", condition_on_previous_text=False)

    with open(text_output_path, 'w') as f:

        for segment in segments:
            f.write("[%.2fs -> %.2fs] %s \n" % (segment.start, segment.end, segment.text))

            
summary_text_output_path = "./output/anime_episode/text/summary.txt"

transcribe_audio(model, input_audio_path, summary_text_output_path)
    
