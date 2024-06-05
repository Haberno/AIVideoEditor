import os
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image

# Initialize CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def parse_timestamp(filename):
    # Extract the timestamp from filenames like "frame_7.16.jpg"
    base = os.path.basename(filename)
    timestamp = base.replace('frame_', '').replace('.jpg', '')
    return float(timestamp)

def find_best_matching_frame(transcription, start_time, end_time, images_dir):
    # Calculate the midpoint of the transcription segment
    mid_time = start_time + end_time
    start_range = max(0, mid_time - 30)
    end_range = min(1583.82,mid_time + 30)

    # Load and preprocess only images within the 30-second window
    images = []
    filenames = []


    for filename in os.listdir(images_dir):
        if filename.endswith(".jpg"):
            frame_time = parse_timestamp(filename)
            if start_range <= frame_time <= end_range:
                path = os.path.join(images_dir, filename)
                image = Image.open(path).convert("RGB")
                images.append(image)
                filenames.append(filename)

    if not images:  # Check if the images list is empty
        print("No images found in the specified time range.")
        return "No images available"


    inputs = processor(text=[transcription], images=images, return_tensors="pt", padding=True)
    outputs = model(**inputs)

    logits_per_image = outputs.logits_per_image  # this scores how well each image matches the text


    print(logits_per_image)
    print(logits_per_image.argmax())
    print (filenames)
    best_image_idx = logits_per_image.argmax().item()

    # Ensure the index is within the bounds of the list
    if best_image_idx < len(filenames):
        print(filenames[best_image_idx])
        return filenames[best_image_idx]
    else:
        return "Computed index out of bounds" 
    


# Path to the transcription file
transcription_file_path = './output/anime_episode/text/summary.txt'
images_dir = './output/anime_episode/images/'

# Process all segments
results = []
with open(transcription_file_path, 'r') as file:
    for line in file:
        parts = line.split(']')
        timestamp_part = parts[0].replace('[', '').split(' -> ')
        start_time = float(timestamp_part[0].replace('s', ''))
        end_time = float(timestamp_part[1].replace('s', ''))
        transcription = parts[1].strip()

        best_frame = find_best_matching_frame(transcription, start_time, end_time, images_dir)
        results.append((transcription, start_time, end_time, best_frame))

# Output results
for result in results:
    print(f"Segment from {result[1]:.2f}s to {result[2]:.2f}s, Transcription: '{result[0]}', Best Frame: {result[3]}")
