import subprocess, json, os

base = r"f:\龙虾机器人\日常定时推送\bedtime-story"
os.chdir(base)

# 1. 检查各章节时长（验证是新生成的小鹿斑斑内容）
print("=== 检查各章节音频 ===")
t = 0.0
timestamps = []
for i in range(1, 9):
    r = subprocess.run(['ffprobe','-v','quiet','-print_format','json','-show_streams',f'audio/ch{i}.mp3'], capture_output=True, text=True)
    d = float(json.loads(r.stdout)['streams'][0]['duration'])
    timestamps.append((round(t, 3), round(t + d, 3)))
    print(f'ch{i}: {d}s')
    t += d
print(f'Total: {round(t, 1)}s')

# 2. 用绝对路径写 concat 文件
with open('audio/concat_list.txt', 'w', encoding='utf-8') as f:
    for i in range(1, 9):
        abs_path = os.path.abspath(f'audio/ch{i}.mp3')
        f.write(f"file '{abs_path}'\n")
print('concat_list.txt 写好了')

# 打印 concat 内容确认
with open('audio/concat_list.txt', 'r', encoding='utf-8') as f:
    print('concat 内容:')
    print(f.read())

# 3. 合并音频
r2 = subprocess.run([
    'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
    '-i', 'audio/concat_list.txt',
    '-acodec', 'copy',
    'audio/full.mp3'
], capture_output=True, text=True)
if r2.returncode != 0:
    print(f'ffmpeg 失败: {r2.stderr[-500:]}')
else:
    print('ffmpeg 合并成功!')

# 4. 验证
r3 = subprocess.run(['ffprobe','-v','quiet','-print_format','json','-show_streams','audio/full.mp3'], capture_output=True, text=True)
dur = json.loads(r3.stdout)['streams'][0]['duration']
print(f'full.mp3 最终时长: {dur}s')

# 5. 更新 index.html
chapter_texts = [
    "森林深处住着一只温柔的小鹿斑斑。她有一双闪闪发光的大眼睛，身上布满了阳光般的斑点。斑斑有一个特别的本领，她能在月光下看到别人看不见的东西，比如飘浮在夜空中的梦境泡泡。",
    "一天晚上，斑斑发现一只小松鼠在树洞里翻来覆去睡不着。斑斑走过去轻轻问：你怎么啦？小松鼠说：我做了一个可怕的梦，不敢再睡了。斑斑心疼地说：别怕，我帮你找一个美美的梦。",
    "斑斑带着小松鼠来到一片从未见过的秘密花园。花园里开满了会发光的花朵，每朵花里都藏着一个美梦。萤火虫在花丛中飞舞，把花园照得像童话世界一样美丽。",
    "这朵蓝色花里藏的是海洋的梦，斑斑说，梦里有会唱歌的海豚和彩虹色的珊瑚。小松鼠好奇地凑过去闻了闻，甜甜的梦就像棉花糖一样钻进了他的心里。",
    "他们又找到了一朵粉色的花，里面住着云朵的梦。梦里有软绵绵的云朵床铺，还能躺在上面看星星。小松鼠开心极了，眼睛亮得像天上的小星星。",
    "斑斑把最美的金色花朵摘了下来，那是星星的梦。她轻轻把花瓣放在小松鼠的枕头上，小声念了一句古老的咒语：甜梦来，噩梦走，小松鼠安心睡一宿。",
    "小松鼠很快进入了甜美的梦乡，嘴角露出了幸福的微笑。斑斑又悄悄去了森林里每个睡不着的小伙伴的家，给小兔子、小刺猬和小猫头鹰都送去了不同的梦境花朵。",
    "整个森林都安静下来，只有斑斑还醒着。她坐在月光下，看着满天的梦境泡泡轻轻飘过。她知道每个泡泡里都装着一个好梦，明天还会有更多小伙伴需要她的帮助。斑斑微笑着闭上眼睛，也进入了甜美的梦乡。"
]

chapters_js = "[" + ",".join([
    f'{{title:"第{i+1}章",text:"{chapter_texts[i]}",start:{timestamps[i][0]},end:{timestamps[i][1]}}}'
    for i in range(8)
]) + "]"

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>小鹿斑斑的梦境花园</title>
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
        <h2>小鹿斑斑的梦境花园</h2>
        <button class="start-btn" onclick="startStory()">开始听故事</button>
    </div>
    <div class="container">
        <div class="header">
            <h1>小鹿斑斑的梦境花园</h1>
            <div class="subtitle">温馨的睡前故事</div>
        </div>
        <div class="story-card">
            <div class="chapter-title" id="chapterTitle">第1章</div>
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

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("index.html 更新完成")

# 6. Git 推送
print("\n=== Git 推送 ===")
for cmd in [['git','add','-A'],['git','commit','-m','fix: 修复音频合并','--quiet']]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f'cmd {" ".join(cmd)}: {r.stderr}')
for cmd in [['git','push','origin','main','--quiet']]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f'cmd {" ".join(cmd)} failed: {r.stderr[-200:]}')
        print("Git push 失败，网络问题，稍后重试")
    else:
        print("Git push 成功!")

# 7. 飞书推送
print("\n=== 飞书推送 ===")
import urllib.request
webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"
card = {
    "msg_type": "interactive",
    "card": {
        "header": {"title": {"tag": "plain_text", "content": "晚安故事来啦~"}, "template": "orange"},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": "**小鹿斑斑的梦境花园**\n一只小鹿在神秘花园中收集梦境种子，为朋友们编织甜美梦境的温暖故事"}},
            {"tag": "action", "actions": [
                {"tag": "button", "text": {"tag": "plain_text", "content": "点击收听"}, "type": "primary", "url": "https://zhengcls.github.io/bedtime-story/"}
            ]}
        ]
    }
}
data = json.dumps(card, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(webhook, data=data, headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(resp.read().decode('utf-8'))
except Exception as e:
    print(f"飞书推送失败: {e}")

print("\n全部完成!")
