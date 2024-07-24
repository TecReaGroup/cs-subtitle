import os
from tqdm import tqdm
from library import translate


# 定义一个函数来查找具有特定后缀的文件
def find_files(path, suffix):
    found_files = []  # 修改变量名以避免冲突
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.' + suffix):
                found_files.append(os.path.abspath(os.path.join(root, file)))
    return found_files


# 定义一个函数来翻译文件夹中的字幕文件
def translate_subtitles_in_folder(initial_folder_path, translated_folder_path,
                                  api, prompt_path):
    srt_files = find_files(initial_folder_path, suffix='srt')
    for file in tqdm(srt_files):  # 使用tqdm显示进度条
        srt_name = file.split('\\')[-1][:-4]  # 获取不带扩展名的文件名
        path_srt_file = file
        path_srt_translated_file = os.path.join(translated_folder_path,
                                                f"{srt_name}_translated.srt")
        with open(path_srt_file, 'r', encoding='utf-8') as file:
            srt_number = len(file.readlines()) // 4  # 估算字幕数量

        translate.main(path_srt_file, path_srt_translated_file,
                       api, prompt_path, srt_number)  # 调用翻译函数


if __name__ == "__main__":
    prompt_path = r".\prompt\prompt.txt"
    with open("api.key", 'r', encoding='utf-8') as file:
        api = file.readline()
    base_path = r".\subtitle\CS50X\initial"  # 基本路径

    # 遍历基本路径下的所有文件夹
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            initial_folder_path = folder_path
            translated_folder_path = os.path.join(folder_path, "translated")
            os.makedirs(translated_folder_path, exist_ok=True)  # 创建翻译文件夹
            translate_subtitles_in_folder(initial_folder_path,
                                          translated_folder_path,
                                          api, prompt_path)
