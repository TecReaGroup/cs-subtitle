import subprocess
import shutil
import os   


def main(video_name, video_path, srt_translated_path, video_subtitled_folder_path):
    #file path
    video = video_name + '.mp4'
    video_subtitled = video_name + '_subtitled.mp4'
    srt = video_name + '_tanslated.srt'

    #copy files to current folder then use ffmpeg to merge
    shutil.copy(video_path, ".\\")
    shutil.copy(srt_translated_path, ".\\")

    command = f'ffmpeg -hwaccel nvdec -i "{video}" -vf "subtitles={srt}" -preset ultrafast -threads 0 "{video_subtitled}"'
    subprocess.run(command, shell=True)

    #move files to target folder then delete files in current folder
    shutil.move(video_subtitled, video_subtitled_folder_path)
    os.remove(video)
    os.remove(srt)
