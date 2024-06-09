import os
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def parse_timestamp(filename):
    base = os.path.basename(filename)
    timestamp = base.replace('frame_', '').replace('.jpg', '')
    return float(timestamp)

def find_best_matching_frame(transcription, start_time, end_time, images_dir):

    mid_time = (start_time + end_time) * 0.925
    start_range = max(0, mid_time - 30)
    end_range = mid_time + 5

    images = []
    filenames = []

    for filename in os.listdir(images_dir):
        frame_time = parse_timestamp(filename)

        if start_range <= frame_time <= end_range:
            path = os.path.join(images_dir, filename)
            image = Image.open(path).convert("RGB")
            images.append(image)
            filenames.append(filename)


    inputs = processor(text=[transcription], images=images, return_tensors="pt", padding=True)
    outputs = model(**inputs)

    logits_per_image = outputs.logits_per_image 
    probs = logits_per_image.softmax(dim=1)

    # Assuming you have a way to map probabilities to descriptions, this is a simplification

    best_image_idx = logits_per_image.argmax().item()

    print(filenames[best_image_idx])
    return filenames[best_image_idx]
    
    
transcription_file_path = './output/anime_episode/text/aligned_transcription.txt'
images_dir = './output/anime_episode/images/'
matches_dir = "./output/anime_episode/matches/"
output_file_path = os.path.join(matches_dir, 'matches.txt')

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


with open(output_file_path, 'w') as f:
    for result in results:
        transcription, start_time, end_time, best_frame = result
        f.write(f"[{start_time} {end_time}] Transcription: {transcription} Best Matching Frame: {best_frame}\n")
    
