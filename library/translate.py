import itertools
import os
import re
import time
last_time = time.time()


def tanslate(prompt, api):
    import google.generativeai as genai
    global last_time
    if time.time() - last_time < 4:
        time.sleep(4 - (time.time() - last_time))

    genai.configure(api_key=api)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def srt_format(file_path):
    # 定义正则表达式匹配SRT字幕格式
    pattern = re.compile(r'(\d+)\s*\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.+?)\s*(?=\d+\s*\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}|$)', re.DOTALL)

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    matches = pattern.findall(content)
    normalized_subtitles = []

    for match in matches:
        index, start_time, end_time, text = match
        # 分割英文和中文部分
        lines = text.strip().split('\n')
        if len(lines) >= 2:
            english_text = lines[0].strip()
            chinese_text = lines[1].strip()
        else:
            # 如果没有中文翻译，保留原文本
            english_text = text.strip()
            chinese_text = ""

        # 构建规范化字幕格式
        normalized_subtitles.append(f"{index}\n{start_time} --> {end_time}\n{english_text}\n{chinese_text}\n")

    # 将规范化字幕写回文件
    normalized_content = '\n'.join(normalized_subtitles)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(normalized_content)


def find_missing_subtitle_range(file_path, srt_number):
    # 定义正则表达式匹配SRT字幕格式
    pattern = re.compile(r'(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    matches = pattern.findall(content)
    existing_indices = []

    for match in matches:
        index, start_time, end_time = match
        existing_indices.append(int(index))

    existing_indices.sort()

    # 找到缺失的第一段字幕序号
    missing_start_index = None
    missing_end_index = None
    for i in range(1, srt_number + 1):
        if i not in existing_indices:
            if missing_start_index is None:
                missing_start_index = i
            missing_end_index = i
        else:
            if missing_start_index is not None:
                break

    if missing_start_index is not None and missing_end_index is not None:
        return [missing_start_index, missing_end_index]

    return [None, None]


def read_lines_range(file_path, start_num, end_num):
    with open(file_path, 'r', encoding='utf-8') as file:
        missing_txt = ""
        for i in range(1, end_num + 1):
            next_four_lines = list(itertools.islice(file, 4))
            if i >= start_num:
                for line in next_four_lines:
                    missing_txt += line
    return missing_txt


def retranslate(srt_path, srt_translated_path, api, prompt_ask, srt_number):
    with open(srt_translated_path, 'r+', encoding='utf-8') as file:
        missing_subtitle = find_missing_subtitle_range(srt_translated_path,
                                                       srt_number)
        if missing_subtitle[0] is not None:
            srt_tanslate = file.readlines()
            missing_txt = read_lines_range(srt_path, missing_subtitle[0],
                                           missing_subtitle[1])
            prompt = prompt_ask + "\n" + missing_txt
            print(prompt + "\n" + "<< retanslating")

            respond = tanslate(prompt, api)
            with open('temp.srt', 'a+', encoding='utf-8') as file1:
                file1.write(respond+'\n\n')
                file1.seek(0)
                srt_format('temp.srt')
                respond_format = file1.read() + '\n'
            os.remove('temp.srt')
            srt_tanslate.insert((missing_subtitle[0] - 1)*5, respond_format)
            with open(srt_translated_path, 'w', encoding='utf-8') as file:
                file.writelines([str(line) for line in srt_tanslate])
            return 1
        else:
            return 0


def main(srt_path, srt_translated_path, api, prompt_path, srt_number):
    with open(prompt_path, 'r', encoding='utf-8') as file_prompt:
        prompt_ask = file_prompt.read()

    with open(srt_path, 'r', encoding='utf-8') as file1, \
         open(srt_translated_path, 'a+', encoding='utf-8') as file2:
        file2.seek(0)
        srt_translated = file2.readlines()
        file2.seek(0, os.SEEK_END)
        # 获取已经翻译的最后一条字幕序号
        last_position = 0
        for line in reversed(srt_translated):
            if line.strip().isdigit():
                last_position = int(line.strip())
                break

        # 跳过已翻译的字幕块
        for _ in itertools.islice(file1, last_position * 4):
            pass

        flag = find_missing_subtitle_range(srt_translated_path, srt_number)[0]
        srt_split = ""
        while flag:
            for i in range(50):  # 每次读取的最大字幕行数
                next_four_lines = list(itertools.islice(file1, 4))
                if not next_four_lines:
                    flag = False
                    break
                for line in next_four_lines:
                    srt_split += line
                if len(srt_split) > 4000:  # 每次输入的最大字幕字数长度
                    break
            if srt_split == "":
                continue
            prompt = prompt_ask + "\n" + srt_split
            print(prompt + "\n" + "<< translating")
            respond = tanslate(prompt, api)
            file2.write(respond + "\n")
            srt_split = ""
            srt_format(srt_translated_path)

    srt_format(srt_translated_path)
    while retranslate(srt_path, srt_translated_path,
                      api, prompt_ask, srt_number):
        pass


'''  openai api
current_time = time.time()


def chatgpt_tanslate(prompt, chatgpt_api, wait_need=1):
    global current_time
    gap_time = time.time() - current_time    #防止api调用频率过高, 可根据RPM限制进行调整
    if gap_time < 20 and wait_need:
        time.sleep(20-gap_time)
    current_time = time.time()

    from openai import OpenAI
    client = OpenAI(api_key=chatgpt_api)
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        #{"role": "system", "content": None},
        {"role": "user", "content": prompt},
        #{"role": "assistant", "content": None},
    ]
    )
    return completion.choices[0].message.content
'''
