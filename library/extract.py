import os
import datetime
import time
import imageio
import whisper


def seconds_to_hmsm(seconds):
    hours = str(int(seconds // 3600))
    minutes = str(int((seconds % 3600) // 60))
    seconds = seconds % 60
    milliseconds = str(int(int((seconds - int(seconds)) * 1000)))
    seconds = str(int(seconds))
    if len(hours) < 2:
        hours = '0' + hours
    if len(minutes) < 2:
        minutes = '0' + minutes
    if len(seconds) < 2:
        seconds = '0' + seconds
    if len(milliseconds) < 3:
        milliseconds = '0'*(3-len(milliseconds)) + milliseconds
    return f"{hours}:{minutes}:{seconds},{milliseconds}"


def main(video_path, srt_path):
    if os.path.exists(srt_path):  # if srt file exists, skip
        time.sleep(0.01)
        return
    model = whisper.load_model('medium.en')  # whisper model choice
    start_time = datetime.datetime.now()
    print('正在识别：{} --{}'.format('\\'.join(video_path.split('\\')[2:]),
                                start_time.strftime('%Y-%m-%d %H:%M:%S')))
    video = imageio.get_reader(video_path)
    duration = seconds_to_hmsm(video.get_meta_data()['duration'])
    video.close()
    print('视频时长：{}'.format(duration))
    res = model.transcribe(video_path, fp16=False, language='English')
    with open(srt_path, 'w', encoding='utf-8') as f:
        i = 1
        for r in res['segments']:
            f.write(str(i) + '\n')
            f.write(seconds_to_hmsm(float(r['start'])) + ' --> ' +
                    seconds_to_hmsm(float(r['end'])) + '\n')
            f.write(r['text'].strip() + '\n')
            f.write('\n')
            i += 1
    end_time = datetime.datetime.now()
    print('完成识别：{} --{}'.format('\\'.join(video_path.split('\\')[2:]),
                                end_time.strftime('%Y-%m-%d %H:%M:%S')))
    print('花费时间:', end_time - start_time)
