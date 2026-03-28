#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_all.py - 睡前故事一键生成脚本（内置所有防呆检查）

使用方法:
    python fix_all.py

此脚本自动完成:
  1. 读取 index.html 中的 chapters 数组（故事文字已在 index.html 中）
  2. TTS生成音频（防呆A：先删除旧文件）
  3. 获取时间戳 + 合并（防呆B：验证ch*.mp3比full.mp3新）
  4. 验证合并结果（防呆C：检查时长）
  5. 递增音频版本号并更新HTML引用（防呆D：浏览器缓存绕过）

注意事项:
  - 运行前请确保 index.html 中已包含正确的故事章节文字
  - 合并必须在 audio/ 目录内执行（脚本自动 cd）
"""

import asyncio
import edge_tts
import subprocess
import json
import os
import glob
import re
import shutil

PROJECT = r"f:\龙虾机器人\日常定时推送\bedtime-story"
PYTHON = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe"
AUDIO_DIR = os.path.join(PROJECT, "audio")


def log(msg):
    print(f"[fix_all] {msg}")


def get_chapters_from_html():
    """从 index.html 提取 chapters 数组"""
    html_path = os.path.join(PROJECT, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取 chapters = [...] 数组
    import re as re2
    m = re2.search(r"const\s+chapters\s*=\s*(\[.*?\]);", content, re2.DOTALL)
    if not m:
        raise Exception("无法从 index.html 找到 chapters 数组")

    # 用 eval 解析 JS 数组（已知是纯数据）
    chapters = json.loads(m.group(1).replace("'", '"'))
    return chapters


def step1_tts(chapters):
    """第1步：TTS生成音频（防呆A：先删除旧文件）"""
    log("=== 步骤1: TTS生成音频 ===")

    N = len(chapters)
    log(f"检测到 {N} 个章节")

    # 读取旧 full.mp3 时长（用于对比）
    old_full = os.path.join(AUDIO_DIR, "full.mp3")
    old_full_mtime = os.path.getmtime(old_full) if os.path.exists(old_full) else 0
    old_full_dur = 0
    if old_full_mtime:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", old_full],
            capture_output=True, text=True
        )
        try:
            old_full_dur = float(json.loads(r.stdout)["streams"][0]["duration"])
        except:
            pass

    # 逐章生成
    for i, ch in enumerate(chapters):
        path = os.path.join(AUDIO_DIR, f"ch{i+1}.mp3")

        # 【防呆A】：先删除旧文件，否则 edge_tts 可能静默失败
        if os.path.exists(path):
            os.remove(path)
            log(f"  已删除旧 ch{i+1}.mp3")

        communicate = edge_tts.Communicate(ch["text"], "zh-CN-XiaoyiNeural")
        asyncio.run(communicate.save(path))

        # 验证文件确实生成且有内容
        size = os.path.getsize(path)
        if size < 5000:
            raise Exception(f"ch{i+1}.mp3 文件过小({size}字节)，TTS可能生成失败")

        # 验证 mtime 比旧 full.mp3 更新
        mtime = os.path.getmtime(path)
        if mtime <= old_full_mtime:
            raise Exception(f"ch{i+1}.mp3 mtime 未更新，可能写入失败！")

        log(f"  ch{i+1}.mp3 done ({size} bytes)")

    log("TTS生成完成")


def step2_merge_and_verify(chapters):
    """第2步：合并并验证（防呆B+C）"""
    log("=== 步骤2: 合并音频并验证 ===")

    N = len(chapters)
    full_path = os.path.join(AUDIO_DIR, "full.mp3")
    full_mtime = os.path.getmtime(full_path)

    # 【防呆B】：验证所有 ch*.mp3 比 full.mp3 更新
    ch_durations = []
    for i in range(1, N + 1):
        ch_path = os.path.join(AUDIO_DIR, f"ch{i}.mp3")
        ch_mtime = os.path.getmtime(ch_path)
        if ch_mtime <= full_mtime:
            raise Exception(
                f"ch{i}.mp3 比 full.mp3 更旧！"
                f"请确保 TTS 已重新生成（防呆A未生效）"
            )

        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", ch_path],
            capture_output=True, text=True
        )
        dur = float(json.loads(r.stdout)["streams"][0]["duration"])
        ch_durations.append(dur)
        log(f"  ch{i}: {dur:.3f}s")

    expected_total = sum(ch_durations)
    log(f"预期总时长: {expected_total:.1f}s")

    # 写 concat_list.txt（相对路径，从 audio/ 目录执行时用 ch{i}.mp3）
    concat_path = os.path.join(AUDIO_DIR, "concat_list.txt")
    with open(concat_path, "w", encoding="utf-8") as f:
        for i in range(1, N + 1):
            f.write(f"file 'ch{i}.mp3'\n")

    # 在 audio/ 目录内执行合并
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", "concat_list.txt", "-acodec", "copy", "full.mp3"],
        cwd=AUDIO_DIR,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"ffmpeg 合并失败: {str(result.stderr)[-300:]}")

    # 【防呆C】：验证合并结果时长
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", full_path],
        capture_output=True, text=True
    )
    actual_total = float(json.loads(r.stdout)["streams"][0]["duration"])

    if abs(actual_total - expected_total) > 1.0:
        raise Exception(
            f"full.mp3 时长 {actual_total:.1f}s 与预期 {expected_total:.1f}s 差距超过1秒，"
            f"合并可能失败！"
        )

    log(f"合并验证通过！总时长: {actual_total:.1f}s")


def step3_cache_bust(chapters):
    """第3步：递增音频版本号并更新HTML引用（防呆D）"""
    log("=== 步骤3: 浏览器缓存绕过 ===")

    # 找已有的 full_v*.mp3
    existing = glob.glob(os.path.join(AUDIO_DIR, "full_v*.mp3"))
    nums = []
    for f in existing:
        m = re.search(r"full_v(\d+)", os.path.basename(f))
        if m:
            nums.append(int(m.group(1)))
    next_ver = max(nums) + 1 if nums else 2
    new_name = f"full_v{next_ver}.mp3"
    old_name = "full.mp3"
    old_path = os.path.join(AUDIO_DIR, old_name)
    new_path = os.path.join(AUDIO_DIR, new_name)

    # 复制 old 到 new
    shutil.copy(old_path, new_path)

    # 更新 HTML 中的音频引用
    html_path = os.path.join(PROJECT, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 替换 audio/ 引用
    old_ref = f"audio/{old_name}"
    new_ref = f"audio/{new_name}"
    if old_ref in content:
        content = content.replace(old_ref, new_ref)
        log(f"HTML 音频引用: {old_ref} -> {new_ref}")
    else:
        log(f"警告: 未找到 {old_ref}，可能已是新文件名")

    # 同时更新 chapters 数组中的 start/end 时间戳
    timestamps = []
    t = 0.0
    for i, ch in enumerate(chapters):
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams",
             os.path.join(AUDIO_DIR, f"ch{i+1}.mp3")],
            capture_output=True, text=True
        )
        dur = float(json.loads(r.stdout)["streams"][0]["duration"])
        timestamps.append({"title": ch["title"], "start": round(t, 3),
                           "end": round(t + dur, 3), "text": ch["text"]})
        t += dur

    # 替换 chapters 数组
    chapters_js = json.dumps(timestamps, ensure_ascii=False, indent=2)
    # 缩进调整为4空格
    chapters_js = re.sub(r"\n +", lambda m: "\n" + " " * 4 * (len(m.group().rstrip()) // 2), chapters_js)

    content = re.sub(
        r"const\s+chapters\s*=\s*\[.*?\];",
        f"const chapters = {chapters_js};",
        content,
        flags=re.DOTALL
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

    log(f"HTML 已更新（{len(timestamps)}个章节，总时长{round(t,1)}s）")
    log(f"音频版本: {new_name}（已创建，绕过浏览器缓存）")

    return new_name


def main():
    log("========================================")
    log("睡前故事 fix_all.py - 全自动生成（防呆版）")
    log("========================================")

    # 0. 提取 chapters
    chapters = get_chapters_from_html()
    log(f"读取到 {len(chapters)} 个章节: {[c['title'] for c in chapters]}")

    # 1. TTS
    step1_tts(chapters)

    # 2. 合并+验证
    step2_merge_and_verify(chapters)

    # 3. 缓存绕过
    new_audio = step3_cache_bust(chapters)

    log("========================================")
    log(f"全部完成！音频: {new_audio}")
    log("下一步: git add -A && git commit && git push")
    log("========================================")


if __name__ == "__main__":
    main()
