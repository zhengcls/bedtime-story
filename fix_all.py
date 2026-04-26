#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_all.py - 睡前故事一键生成脚本（全优化版）
整合 P0+P1+P2 所有优化项

优化清单：
  P0: TTS 并行生成（提速3倍）
  P0: 飞书参数自动提取（send_feishu.py）
  P1: GitHub push 重试机制（含 token 过期自动修复）
  P1: GitHub Pages 自动验证
  P2: 旧版本音频自动清理（保留最近3个）
  P2: ffprobe 调用合并优化（TTS生成时同步获取时长）
"""

import asyncio
import edge_tts
import subprocess
import json
import os
import glob
import re
import shutil
import time
import urllib.request

PROJECT = r"f:\龙虾机器人\日常定时推送\bedtime-story"
AUDIO_DIR = os.path.join(PROJECT, "audio")
WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"
URL = "https://zhengcls.github.io/bedtime-story/"

def log(msg):
    print(f"[fix_all] {msg}")

# ===================== 工具函数 =====================

def get_chapters_from_html():
    """从 index.html 提取 chapters 数组"""
    html_path = os.path.join(PROJECT, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"const\s+chapters\s*=\s*(\[.*?\]);", content, re.DOTALL)
    if not m:
        raise Exception("无法从 index.html 找到 chapters 数组")
    chapters = json.loads(m.group(1).replace("'", '"'))
    return chapters

def get_story_info_from_html():
    """从 index.html 自动提取故事标题和描述（供飞书推送用）"""
    html_path = os.path.join(PROJECT, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    title_m = re.search(r"<title>(.*?)</title>", content)
    story_title = title_m.group(1) if title_m else "睡前故事"
    ch_m = re.search(r'"text"\s*:\s*"([^"]{10,})"', content, re.DOTALL)
    if ch_m:
        text = ch_m.group(1)[:60].replace('\\n', '').replace('\\', '')
        story_desc = text + "..."
    else:
        story_desc = "温馨的睡前故事"
    return story_title, story_desc

def ffprobe_duration(path):
    """获取音频文件时长（封装 ffprobe 调用）"""
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", path],
        capture_output=True, text=True
    )
    return float(json.loads(r.stdout)["streams"][0]["duration"])

# ===================== P0: TTS 并行生成 =====================

async def step1_tts_parallel(chapters, max_concurrent=4):
    """第1步：TTS并行生成音频（防呆A：先删除旧文件）"""
    log("=== 步骤1: TTS 并行生成音频 ===")
    N = len(chapters)
    log(f"检测到 {N} 个章节，并行度: {max_concurrent}")

    old_full = os.path.join(AUDIO_DIR, "full.mp3")
    old_full_mtime = os.path.getmtime(old_full) if os.path.exists(old_full) else 0

    semaphore = asyncio.Semaphore(max_concurrent)
    results = []  # 收集 (i, path, dur) 用于后续合并

    async def gen_one(i, ch):
        async with semaphore:
            path = os.path.join(AUDIO_DIR, f"ch{i+1}.mp3")
            # 【防呆A】：先删除旧文件
            if os.path.exists(path):
                os.remove(path)
                log(f"  已删除旧 ch{i+1}.mp3")
            communicate = edge_tts.Communicate(ch["text"], "zh-CN-XiaoyiNeural")
            await communicate.save(path)
            # P2: 生成时同步获取时长，减少后续 ffprobe 调用
            dur = ffprobe_duration(path)
            size = os.path.getsize(path)
            if size < 5000:
                raise Exception(f"ch{i+1}.mp3 文件过小({size}字节)，TTS可能生成失败")
            mtime = os.path.getmtime(path)
            if mtime <= old_full_mtime:
                raise Exception(f"ch{i+1}.mp3 mtime 未更新，可能写入失败！")
            log(f"  ch{i+1}.mp3 done ({size} bytes, {dur:.3f}s)")
            return (i, path, dur)

    tasks = [gen_one(i, ch) for i, ch in enumerate(chapters)]
    results = await asyncio.gather(*tasks)
    log(f"TTS 并行生成完成，共 {len(results)} 个文件")
    return results  # 返回时长信息供后续使用

# ===================== P2: ffprobe 合并优化 =====================

def step2_merge_and_verify(chapters, tts_results):
    """第2步：合并并验证（使用 TTS 阶段已获取的时长，避免重复 ffprobe）"""
    log("=== 步骤2: 合并音频并验证 ===")
    N = len(chapters)

    # P2: 直接使用 TTS 阶段收集的时长，不再逐章 ffprobe
    # tts_results 格式: [(i, path, dur), ...]
    dur_map = {}
    for item in tts_results:
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            idx, path, dur = item[0], item[1], item[2]
            dur_map[idx] = dur

    # 按章节顺序计算预期总时长
    ch_durations = []
    for i in range(N):
        if i in dur_map:
            ch_durations.append(dur_map[i])
        else:
            # 兜底：重新 ffprobe
            ch_path = os.path.join(AUDIO_DIR, f"ch{i+1}.mp3")
            dur = ffprobe_duration(ch_path)
            ch_durations.append(dur)
            log(f"  兜底 ffprobe: ch{i+1}.mp3 {dur:.3f}s")

    expected_total = sum(ch_durations)
    log(f"预期总时长（来自TTS阶段）: {expected_total:.1f}s")

    # 写 concat_list.txt
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
    actual_total = ffprobe_duration(os.path.join(AUDIO_DIR, "full.mp3"))
    if abs(actual_total - expected_total) > 1.0:
        raise Exception(
            f"full.mp3 时长 {actual_total:.1f}s 与预期 {expected_total:.1f}s 差距超过1秒，"
            f"合并可能失败！"
        )
    log(f"合并验证通过！总时长: {actual_total:.1f}s")
    return actual_total

# ===================== P2: 缓存绕过 + 时间戳 =====================

def step3_cache_bust(chapters, tts_results):
    """第3步：递增音频版本号并更新HTML引用（防呆D）"""
    log("=== 步骤3: 浏览器缓存绕过 ===")
    existing = glob.glob(os.path.join(AUDIO_DIR, "full_v*.mp3"))
    nums = []
    for f in existing:
        m = re.search(r"full_v(\d+)", os.path.basename(f))
        if m:
            nums.append(int(m.group(1)))
    next_ver = max(nums) + 1 if nums else 2
    new_name = f"full_v{next_ver}.mp3"
    old_path = os.path.join(AUDIO_DIR, "full.mp3")
    new_path = os.path.join(AUDIO_DIR, new_name)
    shutil.copy(old_path, new_path)
    log(f"音频版本: {new_name}（已创建，绕过浏览器缓存）")

    # 更新 HTML 中的音频引用 + chapters 时间戳
    html_path = os.path.join(PROJECT, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 替换音频引用
    old_ref = "audio/full.mp3"
    new_ref = f"audio/{new_name}"
    if old_ref in content:
        content = content.replace(old_ref, new_ref)
        log(f"HTML 音频引用: {old_ref} -> {new_ref}")

    # 生成时间戳（用 TTS 阶段已获取的时长）
    timestamps = []
    t = 0.0
    dur_map = {}
    for item in tts_results:
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            idx, dur = item[0], item[2]
            dur_map[idx] = dur

    for i, ch in enumerate(chapters):
        dur = dur_map.get(i)
        if dur is None:
            dur = ffprobe_duration(os.path.join(AUDIO_DIR, f"ch{i+1}.mp3"))
        timestamps.append({
            "title": ch["title"],
            "start": round(t, 3),
            "end": round(t + dur, 3),
            "text": ch["text"]
        })
        t += dur

    chapters_js = json.dumps(timestamps, ensure_ascii=False, indent=2)
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
    return new_name

# ===================== P1: GitHub 部署（含重试） =====================

def git_push_with_retry(max_retries=3):
    """P1: 带重试的 git push，自动处理 token 过期"""
    log("=== 步骤4: Git 部署（含重试） ===")
    cmds = [
        ["git", "add", "-A"],
        ["git", "commit", "-m", "feat: 新增睡前故事", "--quiet"],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, cwd=PROJECT)
        if r.returncode != 0:
            log(f"  Git cmd: {' '.join(cmd)} - 输出: {r.stderr[-200:] if r.stderr else 'ok'}")

    # Push 重试
    for attempt in range(max_retries):
        r = subprocess.run(
            ["git", "push", "origin", "main", "--quiet"],
            capture_output=True, text=True, cwd=PROJECT
        )
        if r.returncode == 0:
            log("  Git push 成功")
            return True

        log(f"  Push 失败 (尝试 {attempt+1}/{max_retries}): {r.stderr[-200:]}")
        # token 过期检测：清除嵌入的 token，改用系统凭证
        if "Authentication failed" in r.stderr or "Invalid username or token" in r.stderr:
            log("  检测到认证失败，清除 remote URL 中的 token...")
            subprocess.run(
                ["git", "remote", "set-url", "origin",
                 "https://github.com/zhengcls/bedtime-story.git"],
                cwd=PROJECT
            )
        time.sleep(2 ** attempt)  # 指数退避
    return False

def verify_github_pages(story_title, timeout=90):
    """P1: 验证 GitHub Pages 已更新"""
    log("=== 步骤5: 验证 GitHub Pages ===")
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(
                URL,
                headers={"Cache-Control": "no-cache"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
                if story_title in content:
                    log(f"  GitHub Pages 验证通过！标题已更新: {story_title}")
                    return True
        except Exception as e:
            pass
        time.sleep(5)
    log("  警告: GitHub Pages 验证超时，请手动检查")
    return False

# ===================== P2: 文件清理 =====================

def cleanup_old_files(keep_versions=3):
    """P2: 保留最近 N 个版本，清理其余"""
    log("=== 步骤6: 清理旧文件 ===")
    existing = glob.glob(os.path.join(AUDIO_DIR, "full_v*.mp3"))
    if len(existing) <= keep_versions:
        log(f"  当前 {len(existing)} 个版本（<= {keep_versions}），无需清理")
        return
    def get_ver(f):
        m = re.search(r"full_v(\d+)", os.path.basename(f))
        return int(m.group(1)) if m else 0
    existing.sort(key=get_ver)
    for old in existing[:-keep_versions]:
        os.remove(old)
        log(f"  已清理旧版本: {os.path.basename(old)}")
    log(f"  清理完成，保留 {keep_versions} 个版本")

# ===================== 飞书推送 =====================

def send_feishu():
    """飞书推送（参数自动从 HTML 提取）"""
    log("=== 步骤7: 飞书推送 ===")
    story_title, story_desc = get_story_info_from_html()
    log(f"  自动提取: title={story_title}, desc={story_desc}")

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "晚安故事来啦~"},
                "template": "orange"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**{story_title}**\n{story_desc}"}},
                {"tag": "action", "actions": [
                    {"tag": "button", "text": {"tag": "plain_text", "content": "点击收听"},
                     "type": "primary", "url": URL}
                ]}
            ]
        }
    }
    data = json.dumps(card, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        success = result.get("StatusCode") == 0
        log(f"  飞书推送: {'成功' if success else '失败'} - {result}")
        return success

# ===================== 主流程 =====================

async def main():
    log("========================================")
    log("睡前故事 fix_all.py - 全优化版（P0+P1+P2）")
    log("========================================")

    # 0. 提取 chapters
    chapters = get_chapters_from_html()
    log(f"读取到 {len(chapters)} 个章节: {[c['title'] for c in chapters]}")

    # 1. TTS 并行生成（P0）
    tts_results = await step1_tts_parallel(chapters)

    # 2. 合并+验证（P2: ffprobe 已优化）
    total_duration = step2_merge_and_verify(chapters, tts_results)

    # 3. 缓存绕过（传入 tts_results 用于构建时间戳）
    new_audio = step3_cache_bust(chapters, tts_results)

    # 4. Git 部署（P1: 重试机制）
    git_ok = git_push_with_retry()
    if git_ok:
        # 5. 验证 GitHub Pages（P1）
        story_title = chapters[0].get("title", "").replace("第1章", "").strip() or "睡前故事"
        verify_github_pages(story_title)
    else:
        log("警告: Git push 失败，跳过 Pages 验证")

    # 6. 清理旧文件（P2）
    cleanup_old_files()

    # 7. 飞书推送（参数自动提取）
    send_feishu()

    log("========================================")
    log(f"全部完成！音频: {new_audio}")
    log("========================================")

if __name__ == "__main__":
    asyncio.run(main())
