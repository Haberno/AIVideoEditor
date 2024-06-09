import os
import subprocess

# Function to clip video segments
def clip_video_segment(input_video_path, start_time, end_time, output_path):
    command = [
        "ffmpeg",
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_video_path,
        "-c:v", "h264_nvenc",
        "-c:a", "aac",
        "-y",  # Overwrite output files without asking
        output_path
    ]
    subprocess.run(command, check=True)

# Paths and filenames
input_video_path = "inputs/anime_episode.mp4"
matches_file_path = "./output/anime_episode/matches/matches.txt"
output_dir = "./output/anime_episode/clips/"

# Ensure output directory exists

# Process the matches file and clip the video segments
try:
    with open(matches_file_path, 'r') as file:
        index = 0
        for line in file:
            parts = line.split('Transcription: ')
            if len(parts) == 2:
                time_part, frame_part = parts[0].strip(), parts[1].strip()
                time_part = time_part.replace('[', '').replace(']', '')
                times = time_part.split(' ')
                start_time = float(times[0])
                end_time = float(times[1])
                duration = end_time - start_time

                # Extract and clean the frame timestamp from the "Best Matching Frame" information
                frame_time_str = frame_part.split('frame_')[1].split('.jpg')[0]
                frame_time = float(frame_time_str.strip('.'))
                
                # Calculate new start and end times around the frame timestamp
                new_start_time = frame_time 
                new_end_time = frame_time + duration
                
                # Define the output file name
                output_file_name = f"clip_{index}.mp4"
                output_path = os.path.join(output_dir, output_file_name)
                

                index += 1
                # Clip the video segment
                clip_video_segment(input_video_path, new_start_time, new_end_time, output_path)
                print(f"Created clip: {output_path}")
                
except Exception as e:
    print(f"An error occurred: {e}")
