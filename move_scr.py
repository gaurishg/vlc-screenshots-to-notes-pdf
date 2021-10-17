# Import os module to list files
import os
# high level path manipulations and globbing
from pathlib import Path, PurePath
import shutil
import glob


"""
1. Save video name into a variable
2. Check if 'Done' Folder is in current folder or not
3. If not then make it and cd into it otherwise directly cd into it
4. make a folder with the video name excluding extension
5. cd into the folder
6. move all screenshots to this folder
7. move video here too"""


# Base directory where screenshots are saved
screenshot_dir = r"D:\Pictures"

# Prefix of screenshots
prefix_of_screenshots = 'vlcsnap'

# picture file extension
pic_extension_with_dot = '.jpg'

# video extension
vid_extension_with_dot = ".mp4"

# current directory
base_dir_path = os.path.abspath('.')

def get_list_of_all_snapshots():
    # l = glob.glob(screenshot_dir + 
    #     f"\\{prefix_of_screenshots}-*{pic_extension_with_dot}")
    l = glob.glob(f"{screenshot_dir}/{prefix_of_screenshots}*{pic_extension_with_dot}")
    return l

print(get_list_of_all_snapshots())
# Get first video name
video_name_with_extension = sorted(glob.glob(f"*{vid_extension_with_dot}"))
# If there is no video with this extension
if not video_name_with_extension:
# close the program
    print(f"No video found with extension {vid_extension_with_dot}")
    exit(0)
# Otherwise grab the first video
else:
    video_name_with_extension = video_name_with_extension[0]
    # remove extension from the name
    video_name_with_extension = os.path.basename(video_name_with_extension)
    video_name_without_extension = os.path.splitext(video_name_with_extension)[0]

print(video_name_with_extension)


# Check if 'Done' folder exists
if not os.path.exists('Done'):
    # make the folder
    os.mkdir('Done')

# Move into the 'Done' folder
os.chdir('Done')


# Check if 'video_name' folder exists
if not os.path.exists(video_name_without_extension):
    os.mkdir(video_name_without_extension)

# Move into the folder
os.chdir(video_name_without_extension)
print(os.path.abspath(os.curdir))

# Move video into the folder
shutil.move(os.path.join(base_dir_path, video_name_with_extension), '.')

# Move screenshots into the folder
for screenshot in get_list_of_all_snapshots():
    shutil.move(screenshot, '.')