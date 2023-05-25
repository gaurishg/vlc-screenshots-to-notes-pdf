# VLC Screenshots To Notes PDF

If you don't want to waste time writing notes while watching lectures, you can just take screenshot of the video (only from VLC media player) and after the video is over, you can transform those to PDF file for easy reading.

# Requirements
- Python3.10
- PyPDF2
- PIL

# How to use
Let's suppose your lecture videos are stored in a directory named `lecture-videos`
```bash
# Go inside the directory lecture-videos
# Let's say the folder structure is as follow
# ./
# Module 01/
# |- Lecture 01\video1.mp4
# |- Lecture 02\video2.mp4

# Move all screenshots
python -m move_scr.py

# It will make a new folder name 'Done' where it will move the video file as well are screenshots
# Make PDF
python -m create_pdf.py
```

# Environment variables
In the folder where code is stored, make a `.env`
- SCREENSHOT_DIR=*Address of the folder when screenshots are stored*
