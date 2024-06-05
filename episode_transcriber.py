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
    os.makedirs(text_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    
    text_dir = os.path.join(text_dir, f"{video_file_name}.txt")

    return text_dir, image_dir


model_size = "large-v3"
model = WhisperModel(model_size, device="cuda", compute_type="float16")

def transcribe_audio_extract_images(model, video_file, text_output_path, image_output_path) :
    segments, info = model.transcribe(video_file, beam_size=5, language="en", condition_on_previous_text=False)

    with open(text_output_path, 'w') as f:

        for segment in segments:
            f.write("[%.2fs -> %.2fs] %s \n" % (segment.start, segment.end, segment.text))

            # Calculate duration of the segment
            duration = segment.end - segment.start
            
            # Divide the duration into four equal parts to find three equidistant points
            part_duration = duration / 4
            frame_times = [
                segment.start + part_duration,
                segment.start + 2 * part_duration,
                segment.start + 3 * part_duration
            ]
            
            # Extract frames at calculated times
            for frame_time in frame_times:
                output_file = f"{image_output_path}/frame_{frame_time}.jpg"
                subprocess.run([
                    "ffmpeg",
                    "-ss", str(frame_time),
                    "-i", video_file,
                    "-frames:v", "1",
                    "-q:v", "2",
                    output_file
                ], check=True)



input_video_path = "inputs/anime_episode.mp4"
input_audio_path = "inputs/summary.mp3"
base_path = "output"

# Create directories based on the input video file
text_output_path, image_output_path = create_directories(base_path, os.path.basename(input_video_path))

# Run the transcription and image extraction
transcribe_audio_extract_images(model, input_video_path, text_output_path, image_output_path)
    


def transcribe_audio(model, audio_file, text_output_path) :
    segments, info = model.transcribe(audio_file, beam_size=5, language="en", condition_on_previous_text=False)

    with open(text_output_path, 'w') as f:

        for segment in segments:
            f.write("[%.2fs -> %.2fs] %s \n" % (segment.start, segment.end, segment.text))

            
# Run the transcription and image extraction
summary_text_output_path = "./output/anime_episode/text/summary.txt"

transcribe_audio(model, input_audio_path, summary_text_output_path)
    
