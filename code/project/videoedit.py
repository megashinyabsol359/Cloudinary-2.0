from moviepy.editor import VideoFileClip
import os
from flask import current_app


def trim_video_function(videofile, start_time, end_time, trimmed_filename):
    clip = VideoFileClip(os.path.join(current_app.config["UPLOAD_FOLDER"], videofile))
    trimmed_filename_with_extension = f"{trimmed_filename}.mp4"
    trimpath = os.path.join(current_app.config["UPLOAD_FOLDER"], trimmed_filename_with_extension)
    trimmed_clip = clip.subclip(start_time, end_time)
    trimmed_clip.write_videofile(trimpath)
    return trimpath
