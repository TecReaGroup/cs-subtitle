import subprocess
import shutil
import os


def main(video_name, video_path, srt_translated_path,
         video_subtitled_folder_path):
    # file path
    video = video_name + '.mp4'
    video_subtitled = video_name + '_subtitled.mp4'
    srt = video_name + '_tanslated.srt'

    # copy files to current folder then use ffmpeg to merge
    shutil.copy(video_path, ".\\")
    shutil.copy(srt_translated_path, ".\\")

    command = f"ffmpeg -hwaccel cuda -i {video} -vf subtitles={srt} -c:\
                v h264_nvenc -c:a copy {video_subtitled}"

    subprocess.run(command, shell=True)

    # move files to target folder then delete files in current folder
    shutil.move(video_subtitled, video_subtitled_folder_path)
    os.remove(video)
    os.remove(srt)


if __name__ == "__main__":
    video_name = "test"
    video_path = r".\video\test.mp4"
    srt_translated_path = r".\subtitle\test_translated.srt"
    video_subtitled_folder_path = r".\video"

    main(video_name, video_path, srt_translated_path)
