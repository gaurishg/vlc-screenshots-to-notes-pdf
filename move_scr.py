# Import os module to list files
import os
import shutil
import glob
from typing import Callable
from dotenv import load_dotenv

load_dotenv()


DONE = "Done" # Name of the folder where videos go after you have watched them
SCREENSHOT_DIR = os.environ['SCREENSHOT_DIR'] # Base directory where screenshots are saved
PREFIX_OF_SCREENSHOTS = 'vlcsnap' # Prefix of screenshots
PIC_EXTENSIONS_WITH_DOT = ['.jpg', '.png'] # picture file extension
VID_EXTENSION_WITH_DOT = ".mp4"
BASE_DIR_PATH = os.path.abspath('.')


def ignore_folder(x: str) -> bool:
    return (x.startswith(".")) or (x in [DONE, "__pycache__"]) or (x.startswith("__"))


def get_list_of_all_snapshots():
    l: list[str] = []
    for ext in PIC_EXTENSIONS_WITH_DOT:
        l += glob.glob(f"{SCREENSHOT_DIR}/{PREFIX_OF_SCREENSHOTS}*{ext}")
    return l


def get_path_of_first_video(vid_ext: str = VID_EXTENSION_WITH_DOT, ignore_func: Callable[[str], bool]=ignore_folder) -> str | None:
    """
        Check all folders other than those are ignored and find the first video to be moved
    """
    for cur_dir, folders, files in os.walk(BASE_DIR_PATH, topdown=True):
        folders[:] = [f for f in folders if not ignore_func(f)]
        videos = [f for f in files if f.endswith(VID_EXTENSION_WITH_DOT)]
        if videos:
            return os.path.join(cur_dir, videos[0])
    return None

def make_new_path_for_video(old_path_without_video_name: str, base_dir: str=BASE_DIR_PATH) -> str:
    folder = os.path.relpath(old_path_without_video_name, base_dir)
    return os.path.join(DONE, folder)


def main():
    """
    1. Save video path into a variable
    2. Check if 'Done' Folder is in current folder or not
    3. If not then make it and cd into it otherwise directly cd into it
    4. make a folder hierarchy with the video name excluding extension
    5. cd into the folder
    6. move all screenshots to this folder
    7. move video here too
    """
    print(get_list_of_all_snapshots())

    # Get list of videos
    video_name_with_extension = get_path_of_first_video(vid_ext=VID_EXTENSION_WITH_DOT)

    # If there is no video with this extension
    if not video_name_with_extension:
    # close the program
        print(f"No video found with extension {VID_EXTENSION_WITH_DOT}")
        exit(0)
    # Otherwise grab the first video
    else:
        # remove extension from the name
        video_path = os.path.dirname(video_name_with_extension)
        video_name_with_extension = os.path.basename(video_name_with_extension)
        video_name_without_extension = os.path.splitext(video_name_with_extension)[0]

    print(video_name_with_extension)

    folder_to_move_in = make_new_path_for_video(video_path)


    # Check if 'Done' folder exists
    if not os.path.exists(folder_to_move_in):
        # make the folder with all folders inside it
        os.makedirs(folder_to_move_in)

    # Move into the 'Done' folder
    os.chdir(folder_to_move_in)


    # Check if 'video_name' folder exists
    if not os.path.exists(video_name_without_extension):
        os.mkdir(video_name_without_extension)

    # Move into the folder
    os.chdir(video_name_without_extension)
    print(os.path.abspath(os.curdir))

    # Move video into the folder
    shutil.move(os.path.join(video_path, video_name_with_extension), '.')

    # Move screenshots into the folder
    for screenshot in get_list_of_all_snapshots():
        shutil.move(screenshot, '.')



if __name__ == '__main__':
   main()
