# 项目记忆 - 睡前故事推送

> 最后更新：2026-03-28 优化精简，定时任务时间改为 21:30，新规格 7~8章/80~120字 已验证通过

---

## 每日自动化任务完整标准流程（全自动，共7步）

> **执行原则**：全程自动，遇到任何选择自动决定，不询问用户。

---

### 第1步：生成故事内容

- 生成温馨儿童睡前故事，**7~8个章节**
- 每章 **80~120字**，内容适合睡前聆听，治愈温馨
- 主角为可爱小动物，起个好听的名字，避免重复已有故事主角
- 故事名格式：《小XX的XXXXX》
- 不同章节之间要有情节递进，结尾温馨收尾

---

### 第2步：生成音频（必须写 Python 脚本文件执行）

**⚠️ 禁止在命令行直接拼接中文文本，必须写 Python 脚本文件**

**⚠️ 必须先删除旧文件再生成（防呆A）：edge_tts 在目标文件已存在时可能静默失败**

脚本模板（写入 `gen_audio_today.py`，覆盖旧文件）：
```python
import asyncio
import edge_tts
import os

chapters = [
    { "id": 1, "text": "第一章内容..." },
    { "id": 2, "text": "第二章内容..." },
    # ... 按实际章节数填写
]

async def gen():
    for ch in chapters:
        # 【防呆A】：先删除旧文件，edge_tts 不会静默覆盖
        path = f'audio/ch{ch["id"]}.mp3'
        if os.path.exists(path):
            os.remove(path)
        communicate = edge_tts.Communicate(ch["text"], "zh-CN-XiaoyiNeural")
        await communicate.save(path)
        print(f'ch{ch["id"]} done')

asyncio.run(gen())
```

执行命令：
```bash
C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe gen_audio_today.py
```

注意事项：
- 语音：`zh-CN-XiaoyiNeural`（温柔女声）
- 输出：`audio/ch1.mp3` ~ `audio/chN.mp3`（N=实际章节数）
- **Python 脚本中禁用中文引号 `"` `"`，只用英文引号 `"` `'`**
- **print() 中不能含 emoji**，Windows gbk 编码会报 UnicodeEncodeError
- **每次生成前必须删除旧文件**，否则 edge_tts 可能静默写入失败

---

### 第3步：获取时间戳 + 合并为单文件

**⚠️ 核心步骤：解决微信息屏翻章不播放的根本方案**

**⚠️ 必须从 audio/ 目录内执行 ffmpeg，否则 concat_list.txt 路径会出错（防呆B）**

推荐：使用 `fix_all.py` 一键完成第2~5步（包含所有防呆检查）。或手动执行：

写入 `get_timestamps.py`（N 动态适配章节数）：
```python
import subprocess, json, os

# 必须和 gen_audio_today.py 中 chapters 保持相同章节数
N = 8  # 按实际章节数修改（7或8）

# 【防呆B】：先验证 ch*.mp3 比 full.mp3 更新
full_mtime = os.path.getmtime('audio/full.mp3')
for i in range(1, N + 1):
    ch_mtime = os.path.getmtime(f'audio/ch{i}.mp3')
    if ch_mtime <= full_mtime:
        raise Exception(f'ch{i}.mp3 比 full.mp3 更旧，TTS未更新，请重新生成！')

timestamps = []
t = 0
for i in range(1, N + 1):
    r = subprocess.run(
        ['ffprobe','-v','quiet','-print_format','json','-show_streams', f'audio/ch{i}.mp3'],
        capture_output=True, text=True
    )
    duration = float(json.loads(r.stdout)['streams'][0]['duration'])
    timestamps.append((round(t, 3), round(t + duration, 3)))
    print(f'ch{i}: start={round(t,3)} dur={duration:.3f}s')
    t += duration

print(f'Total: {round(t,1)}s')

# 【防呆C】：验证 full.mp3 时长
with open('audio/concat_list.txt', 'w') as f:
    for i in range(1, N + 1):
        f.write(f"file 'ch{i}.mp3'\n")  # 注意：相对于audio/目录，不加前缀
```

然后**在 audio/ 目录内**执行合并：
```bash
cd audio && ffmpeg -y -f concat -safe 0 -i concat_list.txt -acodec copy full.mp3
```

合并后验证（防呆C）：
```python
import subprocess, json
r = subprocess.run(['ffprobe','-v','quiet','-print_format','json','-show_streams','audio/full.mp3'], capture_output=True, text=True)
dur = float(json.loads(r.stdout)['streams'][0]['duration'])
expected = sum(ch_durations)
if abs(dur - expected) > 1:
    raise Exception(f'full.mp3时长{dur}s与预期{expected}s差距过大，合并可能失败！')
print('合并验证通过')
```

---

### 第4步：编写 index.html

**chapters 数组使用时间戳（从第3步输出获取）：**
```javascript
const chapters = [
  { title: "第1章", text: "章节原文...", start: 0, end: 18.6 },
  { title: "第2章", text: "章节原文...", start: 18.6, end: 39.2 },
  // ...
];
```

**关键 JS 逻辑（必须严格照此实现，不能改动结构）：**
```javascript
// 只加载一次，不切换 src
const player = document.getElementById('player');
player.src = "audio/full.mp3";
player.load();

// 开始按钮：必须在用户手势同步调用栈中直接 play()
function startStory() {
  document.getElementById('overlay').style.display = 'none';
  player.currentTime = chapters[0].start;
  player.play().catch(() => {});
}

// 章节切换：只 seek，不换 src
function changeChapter(idx) {
  currentChapter = idx;
  updateChapterUI(idx);
  player.currentTime = chapters[idx].start;
  player.play().catch(() => {});
}

// timeupdate：同步章节 UI + 单章模式自动暂停
player.addEventListener('timeupdate', () => {
  const t = player.currentTime;
  for (let i = chapters.length - 1; i >= 0; i--) {
    if (t >= chapters[i].start) {
      if (currentChapter !== i) updateChapterUI(i);
      break;
    }
  }
  if (!autoPlay) {
    const ch = chapters[currentChapter];
    if (t >= ch.end - 0.2 && currentChapter < chapters.length - 1) {
      player.pause();
    }
  }
});
```

**audio 元素属性（微信兼容必需）：**
```html
<audio id="player" controls preload="auto" playsinline webkit-playsinline
       x5-playsinline x5-video-player-type="h5" x5-video-player-fullscreen="false"></audio>
```

**HTML 编码规则：**
- HTML 标签内容直接写中文，**禁止 Unicode 转义（`\u5c0f` 等）**
- JS 字符串中直接写中文

**页面必备元素：**
- 开始遮罩层（金色脉冲按钮，点击隐藏）
- 原生 audio 控件（含进度条）
- 章节导航按钮组（当前章高亮）
- 上一章 / 下一章按钮
- 自动连播开关（默认开启）
- 深色渐变背景 + 故事文字显示区

---

### 第5步：本地预览验证

```bash
# 后台启动 HTTP 服务
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m http.server 8899"
```

用 `preview_url` 工具打开 `http://localhost:8899`，确认：开始按钮可播、章节切换正常。

---

### 第6步：部署到 GitHub Pages

**⚠️ 必须使用新音频文件名绕过浏览器缓存（防呆D）：**

```bash
# 使用 cache_bust.py 递增版本号并更新HTML引用
cd "f:\龙虾机器人\日常定时推送\bedtime-story"
C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe cache_bust.py
git add -A
git commit -m "feat: 新增睡前故事《故事名》"
git push origin main
```

- 线上地址：https://zhengcls.github.io/bedtime-story/
- **必须执行 cache_bust.py**，否则用户会因浏览器缓存听到旧音频
- 中文路径偶尔 push 失败，失败时重试一次

---

### 第7步：飞书群推送（必须用 Python 脚本）

**⚠️ 禁止用 PowerShell curl（它是 Invoke-WebRequest 别名，处理 JSON 必定出错）**

每次更新 `send_feishu.py` 中的 `story_title` 和 `story_desc`，然后执行：

```python
import urllib.request, json

webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"
story_title = "小XX的XXXXX"     # ← 每次修改
story_desc = "一句话简介"        # ← 每次修改
url = "https://zhengcls.github.io/bedtime-story/"

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
                 "type": "primary", "url": url}
            ]}
        ]
    }
}

data = json.dumps(card, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(webhook, data=data, headers={'Content-Type': 'application/json; charset=utf-8'})
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode('utf-8'))
```

执行：
```bash
C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe send_feishu.py
```

返回 `{"StatusCode":0,"StatusMessage":"success"}` 即为成功。

---

## 关键配置

| 项目 | 值 |
|------|-----|
| 线上地址 | https://zhengcls.github.io/bedtime-story/ |
| 飞书 Webhook | https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66 |
| TTS 语音 | zh-CN-XiaoyiNeural |
| Python 路径 | C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe |
| 音频文件 | audio/ch1.mp3~chN.mp3（分章）+ audio/full_v*.mp3（合并，**每次推送用新文件名**） |
| **定时任务时间** | **每天 21:30** |
| 定时任务工作目录 | f:\龙虾机器人\日常定时推送\bedtime-story |
| **推荐脚本** | **fix_all.py**（一键完成第2~5步，自动包含所有防呆检查） |

## 用户偏好

- **全自动执行**：定时任务中遇到任何需要做选择的情况，自动选择并继续执行，不询问用户确认

---

## 核心技术原理：为什么用合并音频而不是切换 src

**微信/X5内核息屏限制**：手机熄屏后，微信内置浏览器冻结所有网络请求和 DOM 操作。
任何"换 src → load → canplay → play"在息屏下均无效，因为：
- 网络请求被冻结 → 新音频加载不了
- canplay/canplaythrough 永远不触发
- 亮屏后手势 play() 体验极差

**单文件方案为何完美**：
- `audio/full.mp3` 在点击开始时已完整加载（preload="auto"）
- 章节切换只是 `currentTime = seek点`，零网络请求
- 息屏对音频播放完全透明，timeupdate 后台依然触发

---

## 关键Bug修复（必须记）

### Bug3: edge_tts 静默覆盖失败导致TTS不更新
**根因**：当目标文件已存在时，edge_tts 可能在写入时静默失败（文件被占用或权限问题），但不会报错，导致读到旧音频
**解决**：**TTS生成前必须先删除旧的 ch1-ch8.mp3**，再用 edge_tts 写入。绝不能依赖"覆盖"行为

### Bug4: ffmpeg concat路径错误（双层audio/audio/）
**根因**：concat_list.txt写的是相对于项目根目录的路径（`audio/ch1.mp3`），但ffmpeg从audio/目录内执行，找不到`audio/ch1.mp3`
**解决**：concat_list.txt必须写相对于执行目录的路径；从audio/目录内执行时写`ch1.mp3`；或使用cwd参数

### Bug5: 浏览器音频缓存导致用户听到旧音频
**根因**：即使GitHub更新了full.mp3，浏览器会缓存旧的full.mp3，用户每次打开都加载缓存版本
**解决**：每次推送使用**新文件名**（如full_v3.mp3），HTML引用新文件名，彻底绕过浏览器缓存

---

## 强制防呆流程（必须严格遵守）

> 每次定时任务执行时，必须按此顺序执行，否则极大概率产生 Bug3+4+5的连环故障

### 防呆A：TTS生成前强制删除旧文件
```python
# gen_audio.py / gen_audio_today.py 必须包含此逻辑
import os
for i in range(1, 9):
    path = f'audio/ch{i}.mp3'
    if os.path.exists(path):
        os.remove(path)  # 强制删除，否则edge_tts可能静默失败
```

### 防呆B：合并时检查ch*.mp3的mtime，必须比full.mp3更新
```python
# 合并前验证
import os, subprocess, json
for i in range(1, 9):
    ch_mtime = os.path.getmtime(f'audio/ch{i}.mp3')
    full_mtime = os.path.getmtime('audio/full.mp3')
    assert ch_mtime > full_mtime, f'ch{i}.mp3 比 full.mp3 更旧，请重新生成TTS！'
```

### 防呆C：合并后验证full.mp3时长是否符合预期
```python
# 验证总时长
r = subprocess.run(['ffprobe','-v','quiet','-print_format','json','-show_streams','audio/full.mp3'], capture_output=True, text=True)
dur = float(json.loads(r.stdout)['streams'][0]['duration'])
expected = sum_ch_durations()  # ch1~chN时长之和
assert abs(dur - expected) < 1, f'full.mp3时长{dur}s与预期{expected}s差距过大，可能合并失败'
```

### 防呆D：部署时使用新音频文件名
```python
# cache_bust.py - 每次部署递增版本号
import os, glob, re
existing = glob.glob('audio/full_v*.mp3')
nums = [int(re.search(r'full_v(\d+)', f).group(1)) for f in existing]
next_ver = max(nums) + 1 if nums else 2
new_name = f'audio/full_v{next_ver}.mp3'
old_name = 'audio/full.mp3'
# 复制old到new，然后HTML中引用new_name
```
**关键**：concat_list.txt里的源文件也要跟着变！`file 'audio/ch{i}.mp3'` 写法保持不变（ch*.mp3不在缓存范围内）

### 防呆E：部署后最终验证（必做）
```python
# deploy之后执行MD5校验
import hashlib
for fname in ['audio/ch1.mp3', 'audio/full.mp3']:
    with open(fname, 'rb') as f:
        print(fname, hashlib.md5(f.read()).hexdigest())
# 记录到执行日志，如果MD5和上次一样说明TTS/合并出了问题
```



| # | 问题 | 根因 | 解法 |
|---|------|------|------|
| 1 | PowerShell curl 发送飞书失败 | PowerShell curl = Invoke-WebRequest，JSON 特殊字符必定出错 | 统一用 Python urllib 脚本 |
| 2 | TTS 命令行中文乱码 | PowerShell 转义中文引号/逗号失败 | 写 Python 脚本文件，不用命令行拼中文 |
| 3 | HTML 中 Unicode 显示为转义字符 | `\u5c0f` 只在 JS 字符串有效，HTML 文本节点原样显示 | HTML 内容直接写中文，禁止 Unicode 转义 |
| 4 | 开始按钮点击后不播放 | play() 在异步回调中调用，已离开用户手势上下文 | startStory() 同步调用栈中直接 player.play() |
| 5 | 息屏后翻章不自动播放 | X5内核息屏冻结网络，换 src 加载不了 | 合并为单文件 + seek，彻底绕开 |
| 6 | Python print 含 emoji 报错 | Windows 控制台 gbk 不支持 emoji | print() 只用纯中英文 |
| 7 | Python 脚本含中文引号报 SyntaxError | `"` `"` 是全角字符 | 脚本统一用英文引号 `"` `'` |

---

## 故事历史

| 日期 | 故事名 | 状态 |
|------|--------|------|
| 2026-03-27 | 小萤火虫亮亮的星光梦 | 已完成 |
| 2026-03-27 | 小松鼠果果的彩虹桥 | 已完成 |
| 2026-03-27 | 小海龟豆豆的寻星之旅 | 已完成 |
| 2026-03-28 | 小乌龟慢慢的星星花园 | 已完成 |
| 2026-03-28 | 小狐狸橙橙的月亮信 | 已完成（手动补推）|
| 2026-03-28 | 小刺猬团团的萤火虫之夜 | 已完成（新规格 80~120字/8章 首次验证通过）|
| 2026-03-28 | 小熊猫圆圆的竹林音乐会 | 已完成（7章，总时长222s）|
| 2026-03-28 | 小兔子跳跳的星星花园 | 已完成（8章，总时长146.5s）|
| 2026-03-28 | 小猫妙妙的月亮船 | 已完成（8章，总时长120.5s，流水线版首次执行15.5s）|
| 2026-03-28 | 小鹿斑斑的梦境花园 | 已完成（8章，总时长124.5s，流水线12.3s；音频缓存问题修复：使用full_v2.mp3新文件名强制刷新）|
