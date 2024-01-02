from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
from flask import current_app

def trim_video_function(videofile, start_time, end_time):
    clip = VideoFileClip(videofile)

    # Generate a unique filename for the trimed video
    trimmed_filename_with_extension = f"trimed_video.mp4"
    trimed_filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], trimmed_filename_with_extension)

    final_clip = clip.subclip(start_time, end_time)
    final_clip.write_videofile(trimed_filepath, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, fps=24, threads=4)
    return trimed_filepath

def merge_video_function(video1_path, video2_path):
    clip1 = VideoFileClip(video1_path)
    clip2 = VideoFileClip(video2_path)

    # Generate a unique filename for the merged video
    merged_filename_with_extension = f"merged_video.mp4"
    merged_filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], merged_filename_with_extension)

    final_clip = concatenate_videoclips([clip1, clip2])
    final_clip.write_videofile(merged_filepath, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, fps=24, threads=4)

    return merged_filepath
