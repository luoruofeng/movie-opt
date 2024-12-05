import os
import chardet  # 用于自动检测文件编码
import subprocess
import chardet  # 用于自动检测文件编码

# 全局变量，定义 ASS 文件的样式
ASS_STYLE = """
[Script Info]
Title: Converted SRT to ASS
Original Script: Python Script
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Chinese,SimSun,24,&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1
Style: English,Arial,20,&H00FFFF00,&H0000FFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def detect_encoding(file_path):
    """检测文件的编码"""
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
        return result.get("encoding", "utf-8")

def split_text(text):
    """分离中文和英文"""
    import re
    chinese = "".join(re.findall(r"[\u4e00-\u9fff]", text))
    english = " ".join(re.findall(r"[a-zA-Z0-9,.'!? ]+", text))
    return chinese.strip(), english.strip()

def convert_srt_to_ass(srt_file, ass_file):
    """将 SRT 文件转换为 ASS 文件"""
    # 自动检测编码
    encoding = detect_encoding(srt_file)
    print(f"检测到 {srt_file} 的编码为: {encoding}")

    try:
        with open(srt_file, "r", encoding=encoding) as srt, open(ass_file, "w", encoding="utf-8") as ass:
            # 写入 ASS 样式
            ass.write(ASS_STYLE)
            ass.write("\n")

            # 转换内容
            buffer = []  # 用于存储当前字幕块的内容
            for line in srt:
                stripped_line = line.strip()
                if stripped_line.isdigit():  # 检测到字幕序号
                    if buffer:  # 如果有未处理的字幕块，先处理它
                        process_buffer(buffer, ass)
                    buffer = []  # 重置缓冲区
                elif "-->" in stripped_line:  # 检测到时间轴
                    buffer.append(stripped_line)  # 时间轴放入缓冲区
                elif stripped_line:  # 检测到字幕内容
                    buffer.append(stripped_line)  # 字幕内容放入缓冲区

            # 处理最后一块字幕
            if buffer:
                process_buffer(buffer, ass)
    except UnicodeDecodeError as e:
        print(f"文件 {srt_file} 编码错误: {e}")
        print("请手动检查文件编码或使用其他工具转换编码。")

def process_buffer(buffer, ass):
    """处理字幕缓冲区，将其写入 ASS 文件"""
    if len(buffer) < 2:
        return  # 不完整的字幕块，跳过处理

    time_line = buffer[0]
    text = " ".join(buffer[1:]).replace("\n", " ")  # 合并多行字幕内容为一行
    start, end = time_line.split(" --> ")
    start = start.strip().replace(",", ".")
    end = end.strip().replace(",", ".")
    
    chinese, english = split_text(text)
    if chinese:
        ass.write(f"Dialogue: 0,{start},{end},Chinese,,0,0,0,,{chinese}\n")
    if english:
        ass.write(f"Dialogue: 0,{start},{end},English,,0,0,0,,{english}\n")

def srt2ass(args):
    print(f"SRT 文件夹路径: {args.path}")

    # 如果路径为空，则使用当前目录
    path = args.path if args.path else os.getcwd()

    # 检查路径是否存在
    if not os.path.exists(path):
        print(f"路径不存在: {path}")
        return

    # 遍历目录中的所有 SRT 文件
    for file_name in os.listdir(path):
        if file_name.endswith(".srt"):
            srt_file = os.path.join(path, file_name)
            ass_file = os.path.splitext(srt_file)[0] + ".ass"

            print(f"转换文件: {srt_file} -> {ass_file}")
            convert_srt_to_ass(srt_file, ass_file)

    print("转换完成！")



def addass(args):
    print(f"SRT 文件夹路径: {args.path}")

    # 如果路径为空，则使用当前目录
    path = args.path if args.path else os.getcwd()

    # 检查路径是否存在
    if not os.path.exists(path):
        print(f"路径不存在: {path}")
        return

    # 遍历目录中的所有 ASS 文件和视频文件
    ass_files = {os.path.splitext(file)[0]: os.path.join(path, file)
                 for file in os.listdir(path) if file.endswith(".ass")}
    video_files = {os.path.splitext(file)[0]: os.path.join(path, file)
                   for file in os.listdir(path)
                   if file.endswith((".mp4", ".mkv", ".avi", ".mov"))}

    # 为每个视频文件添加对应的字幕
    for video_name, video_path in video_files.items():
        if video_name in ass_files:
            ass_path = ass_files[video_name]
            output_path = os.path.join(path, f"{video_name}_subtitled.mkv")

            # 将路径标准化为相对路径
            relative_ass_path = os.path.relpath(ass_path, start=path)
            relative_video_path = os.path.relpath(video_path, start=path)
            relative_output_path = os.path.relpath(output_path, start=path)
            
            # 使用 ffmpeg 添加字幕
            command = [
                'ffmpeg', '-i', relative_video_path, '-vf', f"ass={relative_ass_path}",
                '-c:a', 'copy', relative_output_path
            ]
            try:
                subprocess.run(command, check=True, cwd=path)  # 指定 cwd 为 path，确保相对路径正确
                print(f"已为视频 {video_name} 添加字幕，保存为 {output_path}")
            except subprocess.CalledProcessError as e:
                print(f"添加字幕失败: {e}")
        else:
            print(f"未找到与视频 {video_name} 对应的 ASS 文件，跳过处理")




def detect_encoding(file_path):
    """检测文件的编码"""
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
        return result.get("encoding", "utf-8")

def read_srt_file(file_path):
    """读取 SRT 文件内容并按字幕块返回"""
    encoding = detect_encoding(file_path)
    with open(file_path, "r", encoding=encoding) as file:
        content = file.read()
    blocks = []
    current_block = []

    for line in content.splitlines():
        if line.strip() == "":
            if current_block:
                blocks.append(current_block)
                current_block = []
        else:
            current_block.append(line)
    
    if current_block:  # 如果最后一个块未添加
        blocks.append(current_block)
    
    return blocks

def write_srt_file(file_path, blocks):
    """将字幕块写入新的 SRT 文件"""
    with open(file_path, "w", encoding="utf-8") as file:
        for idx, block in enumerate(blocks):
            file.write(f"{idx + 1}\n")
            for line in block:
                file.write(line + "\n")
            file.write("\n")

def is_time_equal(block1, block2):
    """检查两个字幕块的时间戳是否相同"""
    time1 = block1[1]
    time2 = block2[1]
    return time1 == time2

def mergesrt(args):
    print(f"SRT 文件夹路径: {args.path}")

    # 如果路径为空，则使用当前目录
    path = args.path if args.path else os.getcwd()

    # 检查路径是否存在
    if not os.path.exists(path):
        print(f"路径不存在: {path}")
        return

    # 获取所有 SRT 文件
    srt_files = [f for f in os.listdir(path) if f.endswith(".srt")]
    merged_files = set()

    for i, file1 in enumerate(srt_files):
        if file1 in merged_files:
            continue
        
        for file2 in srt_files[i+1:]:
            if file2 in merged_files:
                continue
            
            file1_path = os.path.join(path, file1)
            file2_path = os.path.join(path, file2)

            # 读取两个文件内容
            blocks1 = read_srt_file(file1_path)
            blocks2 = read_srt_file(file2_path)

            # 检查时间戳数量和对应的时间是否相同
            if len(blocks1) == len(blocks2) and all(is_time_equal(b1, b2) for b1, b2 in zip(blocks1, blocks2)):
                merged_blocks = []

                for b1, b2 in zip(blocks1, blocks2):
                    # 合并内容
                    time_line = b1[1]  # 时间戳行
                    merged_content = b2[2:] + b1[2:]  # 英文在上，中文在下
                    merged_blocks.append([time_line] + merged_content)

                # 保存新文件
                merged_file_name = os.path.splitext(file1)[0] + "_merged.srt"
                merged_file_path = os.path.join(path, merged_file_name)
                write_srt_file(merged_file_path, merged_blocks)

                # 标记为已处理并删除原文件
                merged_files.add(file1)
                merged_files.add(file2)
                os.remove(file1_path)
                os.remove(file2_path)

                print(f"合并并删除: {file1} 和 {file2} -> {merged_file_name}")
                break
    print("合并完成！")