import os

# Function to dynamically discover .mp4 files from a local directory
def discover_mp4_files(directory):
    mp4_files = []
    for file in os.listdir(directory):
        if file.endswith('.mp4'):
            mp4_files.append(os.path.join(directory, file))
    return mp4_files

# Sample usage
local_directory = './path/to/your/local/directory'
video_files = discover_mp4_files(local_directory)

print(video_files)  # This will print the list of discovered .mp4 files
