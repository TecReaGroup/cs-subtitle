import subprocess


def main(video_name, video_tanslated_name, subtitle_name):
    command = f'''ffmpeg -hwaccel cuda -i {video_name} -vf "subtitles={subtitle_name}:force_style='FontName=Microsoft YaHei,FontSize=15,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=1,Shadow=1,Alignment=2'" -c:v h264_nvenc -c:a copy {video_tanslated_name}'''
    subprocess.run(command, shell=True)


if __name__ == "__main__":
    video_name = "1.mp4"
    video_tanslated_name = "1_tanslated.mp4"
    subtitle_name = "1.srt"
    main(video_name, video_tanslated_name, subtitle_name)
