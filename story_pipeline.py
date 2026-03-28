#!/usr/bin/env python3
"""
睡前故事推送流水线 - 优化版
将7步流程整合为单一脚本，减少进程启动开销
"""

import asyncio
import edge_tts
import subprocess
import json
import os
import sys
import urllib.request
import re
from pathlib import Path

# ============ 配置区 ============
PYTHON_EXE = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe"
WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"
URL = "https://zhengcls.github.io/bedtime-story/"
AUDIO_DIR = Path("audio")
CHAPTERS_COUNT = 8

# ============ 故事内容（2026-03-28）============
STORY_TITLE = "小猫妙妙的月亮船"
STORY_DESC = "一只小猫建造月亮船，踏上星空冒险的温馨故事"

CHAPTERS = [
    {"id": 1, "text": "森林里住着一只可爱的小猫妙妙。她最喜欢在夜晚仰望星空，总是好奇月亮上有什么。这天晚上，一颗流星划过夜空，妙妙许下愿望：她想要一艘月亮船。"},
    {"id": 2, "text": "第二天早晨，妙妙在河边发现了一片闪着银光的贝壳。她高兴极了，决定用这些贝壳建造一艘小船。她邀请小鸟帮忙捡树枝，请小兔子帮忙找藤蔓，大家一起忙碌起来。"},
    {"id": 3, "text": "经过三天的努力，月亮船终于造好了。妙妙在船头系上一根闪亮的星星绳子，这是萤火虫朋友们赠送的礼物。夜幕降临，妙妙轻轻推动小船，驶向了远方。"},
    {"id": 4, "text": "小船漂啊漂，来到了萤火虫山谷。萤火虫们点亮翅膀，为妙妙照亮前行的路。他们唱着歌：妙妙加油向着月亮出发！妙妙开心地挥动手臂表示感谢。"},
    {"id": 5, "text": "继续前行，妙妙遇到了正在巡逻的猫头鹰爷爷。猫头鹰爷爷问她：妙妙，你要去哪里呀？妙妙说：我要去月亮上看看！猫头鹰爷爷微笑着递给她一片羽毛说：这是通往月亮的地图。"},
    {"id": 6, "text": "有了猫头鹰爷爷的羽毛指引，月亮船加速前进。妙妙看到了云朵上的彩虹桥，还看到了住在星星里的小精灵们。他们都向妙妙招手，欢迎她来到星空世界。"},
    {"id": 7, "text": "终于，月亮船抵达了月亮宫。月亮姐姐温柔地迎接妙妙：欢迎你，可爱的小猫！月亮姐姐送给妙妙一枚月光徽章，让她可以在夜晚发出温柔的光芒。"},
    {"id": 8, "text": "妙妙坐着月亮船回到了森林。她把月光徽章挂在胸前，整个森林都被她的光芒照亮。从那以后，妙妙每天都在星光下给小伙伴们讲述她的冒险故事，大家都听得入了迷。"}
]


# ============ 第2步：音频生成（并行优化） ============
async def gen_audio_parallel(chapters, max_concurrent=4):
    """并行生成音频，加速TTS处理"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def gen_one(ch):
        async with semaphore:
            communicate = edge_tts.Communicate(ch["text"], "zh-CN-XiaoyiNeural")
            await communicate.save(f"audio/ch{ch['id']}.mp3")
            print(f"ch{ch['id']} done")
            return ch["id"]
    
    tasks = [gen_one(ch) for ch in chapters]
    await asyncio.gather(*tasks)

# ============ 第3步：时间戳获取+音频合并（合并优化） ============
def get_timestamps_and_merge(chapter_count):
    """一次性获取时间戳并合并音频，减少FFprobe调用次数"""
    timestamps = []
    t = 0.0
    concat_list = []
    
    for i in range(1, chapter_count + 1):
        audio_file = f"audio/ch{i}.mp3"
        
        # 获取时长
        r = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', audio_file],
            capture_output=True, text=True
        )
        duration = float(json.loads(r.stdout)['streams'][0]['duration'])
        timestamps.append((round(t, 3), round(t + duration, 3)))
        t += duration
        concat_list.append(audio_file)
    
    # 使用ffmpeg concat demuxer（比concat协议更稳定）
    concat_file = "audio/concat_list.txt"
    with open(concat_file, 'w', encoding='utf-8') as f:
        for af in concat_list:
            f.write(f"file '{af}'\n")
    
    # 合并音频
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_file, '-acodec', 'copy', 'audio/full.mp3'
    ], capture_output=True)
    
    # 清理临时文件
    os.remove(concat_file)
    
    print(f"timestamps = {timestamps}")
    print(f"total duration: {round(t, 1)}s")
    
    return timestamps, t

# ============ 第4步：HTML生成（模板化优化） ============
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',sans-serif;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);min-height:100vh;color:#fff;overflow-x:hidden}}
        .container{{max-width:600px;margin:0 auto;padding:20px;min-height:100vh;display:flex;flex-direction:column}}
        .header{{text-align:center;padding:30px 0 20px}}
        .header h1{{font-size:24px;font-weight:600;color:#ffd700;text-shadow:0 2px 10px rgba(255,215,0,0.3);margin-bottom:8px}}
        .header .subtitle{{font-size:14px;color:#a0a0a0}}
        .story-card{{background:rgba(255,255,255,0.05);border-radius:16px;padding:20px;margin:10px 0;border:1px solid rgba(255,255,255,0.1);flex:1;display:flex;flex-direction:column}}
        .chapter-title{{font-size:18px;color:#ffd700;margin-bottom:12px;text-align:center}}
        .chapter-text{{font-size:16px;line-height:1.8;color:#e0e0e0;text-align:justify;flex:1}}
        .audio-section{{background:rgba(255,255,255,0.05);border-radius:16px;padding:16px;margin:10px 0;border:1px solid rgba(255,255,255,0.1)}}
        audio{{width:100%;height:40px;border-radius:20px}}
        .controls{{display:flex;justify-content:center;gap:16px;margin-top:12px;flex-wrap:wrap}}
        .btn{{padding:10px 20px;border:none;border-radius:20px;font-size:14px;cursor:pointer;transition:all 0.3s;background:rgba(255,255,255,0.1);color:#fff}}
        .btn:hover{{background:rgba(255,255,255,0.2);transform:translateY(-2px)}}
        .btn-primary{{background:linear-gradient(135deg,#ffd700,#ffaa00);color:#1a1a2e;font-weight:600}}
        .chapters-nav{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:16px 0}}
        .chapter-btn{{padding:8px 14px;border:1px solid rgba(255,215,0,0.3);border-radius:16px;background:rgba(255,215,0,0.1);color:#ffd700;font-size:13px;cursor:pointer;transition:all 0.3s}}
        .chapter-btn.active{{background:linear-gradient(135deg,#ffd700,#ffaa00);color:#1a1a2e;font-weight:600;border-color:transparent}}
        .autoplay-toggle{{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:12px;font-size:14px;color:#a0a0a0}}
        .toggle-switch{{width:44px;height:24px;background:rgba(255,255,255,0.2);border-radius:12px;position:relative;cursor:pointer;transition:background 0.3s}}
        .toggle-switch.on{{background:#ffd700}}
        .toggle-switch::after{{content:'';position:absolute;width:20px;height:20px;background:#fff;border-radius:50%;top:2px;left:2px;transition:transform 0.3s}}
        .toggle-switch.on::after{{transform:translateX(20px)}}
        .overlay{{position:fixed;top:0;left:0;width:100%;height:100%;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);display:flex;flex-direction:column;justify-content:center;align-items:center;z-index:1000}}
        .overlay h2{{font-size:28px;color:#ffd700;margin-bottom:30px;text-align:center;padding:0 20px}}
        .start-btn{{padding:16px 48px;font-size:18px;background:linear-gradient(135deg,#ffd700,#ffaa00);color:#1a1a2e;border:none;border-radius:30px;cursor:pointer;font-weight:600;animation:pulse 2s infinite}}
        @keyframes pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(255,215,0,0.4)}}50%{{box-shadow:0 0 0 20px rgba(255,215,0,0)}}}}
    </style>
</head>
<body>
    <div class="overlay" id="overlay">
        <h2>{title}</h2>
        <button class="start-btn" onclick="startStory()">开始听故事</button>
    </div>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">温馨的睡前故事</div>
        </div>
        <div class="story-card">
            <div class="chapter-title" id="chapterTitle">{chapter_titles[0]}</div>
            <div class="chapter-text" id="chapterText">{chapter_texts[0]}</div>
        </div>
        <div class="audio-section">
            <audio id="player" controls preload="auto" playsinline webkit-playsinline x5-playsinline x5-video-player-type="h5" x5-video-player-fullscreen="false"></audio>
            <div class="chapters-nav" id="chaptersNav"></div>
            <div class="controls">
                <button class="btn" onclick="prevChapter()">上一章</button>
                <button class="btn btn-primary" onclick="nextChapter()">下一章</button>
            </div>
            <div class="autoplay-toggle">
                <span>自动连播</span>
                <div class="toggle-switch on" id="autoplayToggle" onclick="toggleAutoplay()"></div>
            </div>
        </div>
    </div>
    <script>
        const chapters={chapters_js};
        let currentChapter=0,autoPlay=true;
        const player=document.getElementById('player');
        player.src="audio/full.mp3";player.load();
        function initChaptersNav(){{const nav=document.getElementById('chaptersNav');chapters.forEach((ch,idx)=>{{const btn=document.createElement('button');btn.className='chapter-btn'+(idx===0?' active':'');btn.textContent=ch.title;btn.onclick=()=>changeChapter(idx);nav.appendChild(btn);}});}}
        function updateChapterUI(idx){{currentChapter=idx;document.getElementById('chapterTitle').textContent=chapters[idx].title;document.getElementById('chapterText').textContent=chapters[idx].text;document.querySelectorAll('.chapter-btn').forEach((btn,i)=>btn.classList.toggle('active',i===idx));}}
        function startStory(){{document.getElementById('overlay').style.display='none';player.currentTime=chapters[0].start;player.play().catch(()=>{{}});}}
        function changeChapter(idx){{if(idx<0||idx>=chapters.length)return;currentChapter=idx;updateChapterUI(idx);player.currentTime=chapters[idx].start;player.play().catch(()=>{{}});}}
        function prevChapter(){{if(currentChapter>0)changeChapter(currentChapter-1);}}
        function nextChapter(){{if(currentChapter<chapters.length-1)changeChapter(currentChapter+1);}}
        function toggleAutoplay(){{autoPlay=!autoPlay;document.getElementById('autoplayToggle').classList.toggle('on',autoPlay);}}
        player.addEventListener('timeupdate',()=>{{const t=player.currentTime;for(let i=chapters.length-1;i>=0;i--){{if(t>=chapters[i].start){{if(currentChapter!==i)updateChapterUI(i);break;}}if(!autoPlay&&currentChapter<chapters.length-1){{const ch=chapters[currentChapter];if(t>=ch.end-0.2)player.pause();}}}}}});
        player.addEventListener('ended',()=>{{if(autoPlay&&currentChapter<chapters.length-1)changeChapter(currentChapter+1);}});
        initChaptersNav();
    </script>
</body>
</html>'''

def generate_html(title, chapters_with_timestamps):
    """生成优化后的HTML"""
    chapter_titles = [ch["title"] for ch in chapters_with_timestamps]
    chapter_texts = [ch["text"] for ch in chapters_with_timestamps]
    
    # 构建JS章节数据
    chapters_js = "[" + ",".join([
        f'{{title:"{ch["title"]}",text:"{ch["text"].replace(chr(34), chr(92)+chr(34))}",start:{ch["start"]},end:{ch["end"]}}}'
        for ch in chapters_with_timestamps
    ]) + "]"
    
    html = HTML_TEMPLATE.format(
        title=title,
        chapter_titles=chapter_titles,
        chapter_texts=chapter_texts,
        chapters_js=chapters_js
    )
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("index.html generated")

# ============ 第5步：Git部署（条件优化） ============
def git_deploy(story_title):
    """Git提交并推送，使用--quiet减少输出"""
    cmds = [
        ["git", "add", "-A"],
        ["git", "commit", "-m", f"feat: 新增睡前故事《{story_title}》", "--quiet"],
        ["git", "push", "origin", "main", "--quiet"]
    ]
    
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0 and cmd[1] != "commit":  # commit可能因无变化失败
            print(f"Git cmd failed: {cmd}")
            return False
    
    print("git deploy done")
    return True

# ============ 第6步：飞书推送 ============
def send_feishu(story_title, story_desc):
    """发送飞书消息卡片"""
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
    
    data = json.dumps(card, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        WEBHOOK, 
        data=data, 
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = resp.read().decode('utf-8')
        print(result)
        return json.loads(result).get("StatusCode") == 0

# ============ 主流程 ============
async def run_pipeline():
    """执行完整流水线"""
    import time
    start_time = time.time()
    
    story_title = STORY_TITLE
    story_desc = STORY_DESC
    chapters = CHAPTERS
    
    print("="*50)
    print(f"开始执行: {story_title}")
    print("="*50)
    
    # 确保audio目录存在
    AUDIO_DIR.mkdir(exist_ok=True)
    
    # 第2步：并行生成音频
    print("\n[Step 2] 生成音频...")
    t0 = time.time()
    await gen_audio_parallel(chapters)
    print(f"音频生成耗时: {time.time()-t0:.1f}s")
    
    # 第3步：获取时间戳+合并音频
    print("\n[Step 3] 获取时间戳并合并音频...")
    t0 = time.time()
    timestamps, total_duration = get_timestamps_and_merge(len(chapters))
    print(f"时间戳+合并耗时: {time.time()-t0:.1f}s")
    
    # 合并章节数据和时间戳
    chapters_with_ts = []
    for i, ch in enumerate(chapters):
        chapters_with_ts.append({
            "title": f"第{ch['id']}章",
            "text": ch["text"],
            "start": timestamps[i][0],
            "end": timestamps[i][1]
        })
    
    # 第4步：生成HTML
    print("\n[Step 4] 生成HTML...")
    t0 = time.time()
    generate_html(story_title, chapters_with_ts)
    print(f"HTML生成耗时: {time.time()-t0:.1f}s")
    
    # 第5步：Git部署
    print("\n[Step 5] Git部署...")
    t0 = time.time()
    git_deploy(story_title)
    print(f"Git部署耗时: {time.time()-t0:.1f}s")
    
    # 第6步：飞书推送
    print("\n[Step 6] 飞书推送...")
    t0 = time.time()
    success = send_feishu(story_title, story_desc)
    print(f"飞书推送耗时: {time.time()-t0:.1f}s")
    
    total_time = time.time() - start_time
    print("\n" + "="*50)
    print(f"总耗时: {total_time:.1f}s")
    print(f"故事时长: {total_duration:.1f}s")
    print("="*50)
    
    return success

# ============ 命令行入口 ============
if __name__ == "__main__":
    asyncio.run(run_pipeline())
