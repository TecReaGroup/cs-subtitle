import os
import shutil
from tqdm import tqdm
from library import translate
from library import merge


# translate
def translate_subtitles(subtitle_initial_path, subtitle_translated_path, api, prompt_path):
    with open(subtitle_initial_path, 'r', encoding='utf-8') as file:
        srt_number = len(file.readlines()) // 4  # 估算字幕数量
    translate.main(subtitle_initial_path, subtitle_translated_path, api, prompt_path, srt_number)  # 调用翻译函数


# merge
def merge_subtitle(video_initial_path, subtitle_translated_folder_path, subtitle_translated_path):
    video_name = video_initial_path.split("\\")[-1]
    video_tanslated_name = video_initial_path.split("\\")[-1][:-4] + "_2024_中英双语字幕.mp4"
    subtitle_name = subtitle_translated_path.split("\\")[-1]

    # copy files to current folder then use ffmpeg to merge
    shutil.copy(video_initial_path, ".\\")
    shutil.copy(subtitle_translated_path, ".\\")
    merge.main(video_name, video_tanslated_name, subtitle_name)
    
    # move files to target folder then delete files in current folder
    shutil.move(video_tanslated_name, subtitle_translated_folder_path)
    os.remove(video_name)
    os.remove(subtitle_name)


if __name__ == "__main__":
    base_path = r".\subtitle\CS50X"  # 基本路径
    prompt_path = r".\prompt\prompt.txt"
    with open("api.key", 'r', encoding='utf-8') as file:
        api = file.readline()

    video_initial_folder_path = base_path + "\\video_initial"
    video_translated_folder_path = base_path + "\\video_translated"
    subtitle_initial_folder_path = base_path + "\\subtitle_initial"
    subtitle_translated_folder_path = base_path + "\\subtitle_translated"
    os.makedirs(video_initial_folder_path, exist_ok=True)
    os.makedirs(video_translated_folder_path, exist_ok=True)
    os.makedirs(subtitle_initial_folder_path, exist_ok=True)
    os.makedirs(subtitle_translated_folder_path, exist_ok=True)

    video_files = os.listdir(video_initial_folder_path)
    for video_file in tqdm(video_files, desc="Processing videos"):
        video_name = video_file[:-4]
        # extract pass

        # translate
        subtitle_initial_path = subtitle_initial_folder_path + "\\" + video_name + ".srt"
        subtitle_translated_path = subtitle_translated_folder_path + "\\" + video_name + "_translated.srt"
        if not os.path.exists(subtitle_translated_path):
            translate_subtitles(subtitle_initial_path, subtitle_translated_path, api, prompt_path)

        # merge
        video_initial_path = video_initial_folder_path + "\\" + video_file
        video_translated_path = video_translated_folder_path + "\\" + video_name + "_2024_中英双语字幕.mp4"
        if not os.path.exists(video_translated_path):
            merge_subtitle(video_initial_path, video_translated_folder_path, subtitle_translated_path)
