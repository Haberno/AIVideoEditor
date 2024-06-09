import io

def align_timestamps(input_file, output_file):
    with io.open(input_file, 'r', encoding='utf-8') as infile:
        transcription = infile.readlines()

    aligned_transcription = []
    prev_end_time = 0.0

    for i, line in enumerate(transcription):
        # Parse the line to get the timestamp and the text
        timestamp, text = line.split("] ", 1)
        start_time, end_time = timestamp[1:].split(" ")

        # Convert times to float
        start_time = float(start_time[:-1])  # Remove 's' and convert to float
        end_time = float(end_time[:-1])      # Remove 's' and convert to float

        # Adjust the previous segment's end time if needed
        if i > 0 and aligned_transcription:
            previous_line = aligned_transcription.pop()
            prev_timestamp, prev_text = previous_line.split("] ", 1)
            prev_start_time, _ = prev_timestamp[1:].split(" -> ")
            # Format with adjusted previous end time
            aligned_transcription.append(f"[{prev_start_time} -> {start_time:.2f}s] {prev_text}")

        # Update the previous end time for the next iteration
        prev_end_time = end_time

        # Keep the last line's end time as is
        new_timestamp = f"[{start_time:.2f}s -> {end_time:.2f}s]"
        aligned_transcription.append(f"{new_timestamp} {text}")

    with io.open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("".join(aligned_transcription))

# Example usage
input_file = './output/anime_episode/text/summary.txt'
output_file = './output/anime_episode/text/aligned_transcription.txt'
align_timestamps(input_file, output_file)
