import itertools
import os
import re
import time


def tanslate(prompt, api, wait_time=0):
    time.sleep(wait_time)

    import google.generativeai as genai
    genai.configure(api_key=api)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def is_time_format(s):
    pattern = r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}"
    return bool(re.match(pattern, s))


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


def srt_format(srt_path):
    formatted_lines = []
    with open(srt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if i > len(lines)-4:
                break
            line = lines[i].split('\n')[0]
            if line.isdigit():  # 判断字幕时间格式
                flag_jump = False
                if not is_time_format(lines[i+1].split('\n')[0]):
                    flag_jump = True
                for j in range(2, 4):
                    if lines[i+j].split('\n')[0] == '\n' or \
                       is_time_format(lines[i+j].split('\n')[0]):
                        flag_jump = True
                if flag_jump:
                    continue
                for j in range(4):
                    formatted_lines.append(lines[i+j].strip() + '\n')
                formatted_lines.append('\n')
    with open(srt_path, 'w', encoding='utf-8') as file:
        for line in formatted_lines:
            file.write(line)


def read_lines_range(file_path, start_num, end_num):
    with open(file_path, 'r', encoding='utf-8') as file:
        missing_txt = ""
        for i in range(1, end_num):
            next_four_lines = list(itertools.islice(file, 4))
            if i > start_num:
                for line in next_four_lines:
                    missing_txt += line
    return missing_txt


def retranslate(srt_path, srt_translated_path, api, prompt_ask, srt_number):
    with open(srt_translated_path, 'r+', encoding='utf-8') as file:
        srt_tanslate = file.readlines()
        falg_change = False
        i = 0
        while i+5 < len(srt_tanslate) or i+5 < srt_number*5:
            if i+5 == len(srt_tanslate):  # 字幕末尾遗漏翻译
                j = int(srt_tanslate[i].split('\n')[0])
                k = srt_number + 1
            else:  # 字幕中间遗漏翻译
                j = int(srt_tanslate[i].split('\n')[0])
                k = int(srt_tanslate[i+5].split('\n')[0])
            if j+1 != k:
                retanslate_number = k - j - 1
                if retanslate_number <= 3 and k+3 <= srt_number+1:
                    k += 3
                missing_txt = read_lines_range(srt_path, j, k)
                prompt = prompt_ask + missing_txt
                print(prompt + "\n" + "<< retanslating")
                respond = tanslate(prompt, api)
                with open('temp.srt', 'w', encoding='utf-8') as file:
                    file.write(respond+'\n\n')
                    srt_format('temp.srt')
                with open('temp.srt', 'r', encoding='utf-8') as file:
                    respond_format = file.readlines()
                os.remove('temp.srt')
                lp = i+5
                for m in range(retanslate_number):
                    if m*5 + 4 >= len(respond_format):
                        break
                    for n in range(5):
                        srt_tanslate.insert(lp, respond_format[m*5+n])
                        lp += 1
                falg_change = True
            i += 5
    if falg_change:
        with open(srt_translated_path, 'w', encoding='utf-8') as file:
            file.writelines(srt_tanslate)


def main(srt_path, srt_translated_path, api, prompt_path, srt_number):
    if os.path.exists(srt_translated_path):
        print(f"{srt_path} has been subtitled.")
        return 0
    else:
        os.makedirs(os.path.dirname(srt_translated_path), exist_ok=True)

    with open(srt_path, 'r', encoding='utf-8') as file1, \
         open(srt_translated_path, 'w', encoding='utf-8') as file2, \
         open(prompt_path, 'r', encoding='utf-8') as file3:
        flag = True
        srt_split = ""
        prompt_ask = file3.read()
        while flag:
            for i in range(100):  # 每次读取的最大字幕行数
                next_four_lines = list(itertools.islice(file1, 4))
                if not next_four_lines:
                    flag = False
                    break
                for line in next_four_lines:
                    srt_split += line
                if len(srt_split) > 5000:  # 每次输入的最大字幕字数长度
                    break
            prompt = prompt_ask + srt_split
            print(prompt + "\n" + "<< translating")
            respond = tanslate(prompt, api, 0)
            file2.write(respond + "\n\n")
            srt_split = ""
    srt_format(srt_translated_path)
    retranslate(srt_path, srt_translated_path, api, prompt_ask, srt_number)
    srt_format(srt_translated_path)

    # 检验翻译是否完整
    with open(srt_translated_path, 'r', encoding='utf-8') as file:
        srt_tanslate = file.readlines()
        if len(srt_tanslate)//5 == srt_number:
            print("翻译完整")
        else:
            print("翻译不完整")
