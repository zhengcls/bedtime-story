# 项目记忆 - 睡前故事推送

> 最后更新：2026-03-28 经完整验证后重写，每日自动化任务直接按此执行；故事规格调整为 7~8章/80~120字

---

## 每日自动化任务完整标准流程（全自动，共7步）

### 第1步：生成故事内容
- 生成温馨儿童睡前故事，**7~8个章节**
- 每章 **80~120字**，内容适合睡前聆听，治愈温馨
- 主角为可爱小动物，起个好听的名字
- 故事名格式：《小XX的XXXXX》

故事数据结构（仅供参考，第3步会改成时间戳格式）：
```json
[
  { "title": "第1章", "text": "..." },
  ...
  { "title": "第8章", "text": "..." }
]
```

### 第2步：生成音频（Python edge-tts，写脚本文件执行）

**⚠️ 禁止在命令行直接拼接中文文本，必须写 Python 脚本文件**

脚本模板（写入 `gen_audio_today.py`）：
```python
import asyncio
import edge_tts

chapters = [
    { "id": 1, "text": "第一章内容..." },
    ...
    { "id": 7, "text": "第七章内容..." },
]

async def gen():
    for ch in chapters:
        communicate = edge_tts.Communicate(ch["text"], "zh-CN-XiaoyiNeural")
        await communicate.save(f"audio/ch{ch['id']}.mp3")
        print(f"ch{ch['id']} done")

asyncio.run(gen())
```

执行：`python gen_audio_today.py`

- 语音：`zh-CN-XiaoyiNeural`（女声温柔）
- 输出：`audio/ch1.mp3` ~ `audio/ch7.mp3`（或 ch8.mp3，视章节数而定）
- **Python脚本中不能有中文引号（""），只用英文引号**
- **print() 中不能含 emoji**，Windows gbk 编码会报 UnicodeEncodeError

### 第3步：获取各章节时长，合并为单文件

**⚠️ 这是核心步骤，解决微信息屏翻章不播放问题的根本方案**

```python
import subprocess, json

# 获取各章时长（N = 实际章节数，7或8）
timestamps = []
t = 0
N = len(chapters)  # 按实际章节数动态处理
for i in range(1, N + 1):
    r = subprocess.run(
        ['ffprobe','-v','quiet','-print_format','json','-show_streams',f'audio/ch{i}.mp3'],
        capture_output=True, text=True
    )
    duration = float(json.loads(r.stdout)['streams'][0]['duration'])
    timestamps.append((t, t + duration))
    t += duration

print("章节时间戳：", timestamps)
```

合并命令（7章版本，8章时末尾追加 |audio/ch8.mp3）：
```bash
ffmpeg -y -i "concat:audio/ch1.mp3|audio/ch2.mp3|audio/ch3.mp3|audio/ch4.mp3|audio/ch5.mp3|audio/ch6.mp3|audio/ch7.mp3" -acodec copy audio/full.mp3
# 8章时改为：
# ffmpeg -y -i "concat:audio/ch1.mp3|...|audio/ch8.mp3" -acodec copy audio/full.mp3
```

### 第4步：编写 index.html（基于成熟模板）

**chapters 数组格式（用时间戳，不用 url）：**
```javascript
const chapters = [
  { title: "第1章", text: "...", start: 0, end: 32.18 },
  { title: "第2章", text: "...", start: 32.18, end: 67.34 },
  // ...
  { title: "第7章", text: "...", start: 209.73, end: 248.01 }
];
```

**关键 JS 逻辑（必须完全照此实现）：**
```javascript
// 只加载一次，不切换 src
player.src = "audio/full.mp3";
player.load();

// 开始按钮：在用户手势回调中直接 play()
function startStory() {
  document.getElementById('overlay').style.display = 'none';
  player.currentTime = chapters[0].start;
  player.play().catch(() => {});  // ⚠️ 必须在同一调用栈中 play()
}

// 章节切换：只 seek，不换 src
function changeChapter(idx) {
  player.currentTime = chapters[idx].start;
  player.play().catch(() => {});
}

// timeupdate：同步章节UI
player.addEventListener('timeupdate', () => {
  const t = player.currentTime;
  for (let i = chapters.length - 1; i >= 0; i--) {
    if (t >= chapters[i].start) {
      if (currentChapter !== i) updateChapterUI(i);
      break;
    }
  }
  // 单章模式：到章末暂停
  if (!autoPlay) {
    const ch = chapters[currentChapter];
    if (player.currentTime >= ch.end - 0.2 && currentChapter < chapters.length - 1) {
      player.pause();
    }
  }
});
```

**audio 元素属性（微信兼容）：**
```html
<audio id="player" controls preload="auto" playsinline webkit-playsinline 
       x5-playsinline x5-video-player-type="h5" x5-video-player-fullscreen="false"></audio>
```

**HTML 编码规则：**
- HTML 标签内容（`<title>`、`<div>` 文字等）直接写中文，**禁止 Unicode 转义**
- JS 字符串中直接写中文即可

**页面必备功能：**
- 开始遮罩层（金色脉冲按钮，点击后隐藏）
- 原生 audio 控件（含进度条）
- 章节导航按钮组（第1章~第7章，当前章高亮）
- 上一章 / 下一章按钮
- 自动连播开关（默认开启）
- 深色渐变背景 + 故事文字显示区

### 第5步：本地预览验证（快速）
- 使用 `preview_url` 工具打开本地页面
- 验证：开始按钮能播、章节切换正常、自动连播逻辑对

### 第6步：部署到 GitHub Pages
```bash
git add -A
git commit -m "feat: 新增睡前故事《故事名》"
git push origin main
```
- 中文路径偶尔出问题，失败时重试一次
- 线上地址：https://zhengcls.github.io/bedtime-story/

### 第7步：推送飞书群（Python脚本，禁止用 curl）

**必须用 Python 脚本，PowerShell curl 是 Invoke-WebRequest 别名，处理 JSON 必定失败**

```python
import urllib.request, json

webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"
story_title = "小XX的XXXXX"
story_desc = "一句话简介"
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

执行：`python send_feishu.py`（每次更新 send_feishu.py 中的标题和简介）

---

## 关键配置

| 项目 | 值 |
|------|-----|
| 线上地址 | https://zhengcls.github.io/bedtime-story/ |
| 飞书 Webhook | https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66 |
| TTS 语音 | zh-CN-XiaoyiNeural |
| 音频文件 | audio/ch1.mp3~ch7.mp3（分章）+ audio/full.mp3（合并） |
| 定时任务时间 | 每天 21:45 |
| 定时任务工作目录 | f:\龙虾机器人\日常定时推送\bedtime-story |

## 用户偏好
- **全自动执行**：定时任务中遇到任何需要做选择的情况，自动选择并继续执行，不需要询问用户确认

---

## 核心技术原理：为什么用合并音频而不是切换 src

**微信/X5内核息屏限制**：手机熄屏后，微信内置浏览器会冻结所有网络请求和 DOM 操作。
任何"换 src → load → canplay → play"的方案在息屏状态下都无效，因为：
- 网络请求被冻结 → 新音频文件加载不了
- canplay/canplaythrough 事件永远不触发
- 亮屏后用手势 play() 是最后的救场，但体验极差

**单文件方案为何完美**：
- `audio/full.mp3` 在用户点击开始时就已完整加载（preload="auto"）
- 章节切换只是 `currentTime = seek点`，不涉及任何网络请求
- 息屏对音频播放完全透明——它只是一个持续播放的音频流
- timeupdate 在浏览器后台依然触发，UI 同步完全正常

---

## 踩坑汇总（所有已知问题）

| # | 问题 | 根因 | 解法 |
|---|------|------|------|
| 1 | PowerShell curl 失败 | PowerShell curl = Invoke-WebRequest，处理 JSON 特殊字符必定出错 | 统一用 Python urllib 脚本 |
| 2 | TTS 命令行中文乱码 | PowerShell 转义中文引号/逗号失败 | 写 Python 脚本文件，不用命令行拼中文 |
| 3 | HTML 中 Unicode 转义乱码 | `\u5c0f` 等只在 JS 字符串有效，HTML 文本节点会原样显示 | HTML 内容直接写中文，JS 字符串随意 |
| 4 | 开始按钮点击后不播放 | play() 在异步回调中调用，已离开用户手势上下文 | 在 startStory() 同步调用栈中直接 player.play() |
| 5 | 熄屏后翻章不自动播放 | X5内核息屏冻结网络，换 src 加载不了 | 合并音频为单文件 + seek，彻底绕开 |
| 6 | Python print 含 emoji 报错 | Windows 控制台 gbk 编码不支持 emoji | print() 只用纯中文/英文 |
| 7 | Python 脚本含中文引号报错 | `"` `"` 是全角字符，Python 解析为语法错误 | 脚本中统一用英文引号 `"` `'` |

---

## 故事历史
| 日期 | 故事名 | 状态 |
|------|--------|------|
| 2026-03-27 | 小萤火虫亮亮的星光梦 | 已完成 |
| 2026-03-27 | 小松鼠果果的彩虹桥 | 已完成 |
| 2026-03-27 | 小海龟豆豆的寻星之旅 | 已完成 |
| 2026-03-28 | 小乌龟慢慢的星星花园 | 已完成 |
| 2026-03-28 | 小狐狸橙橙的月亮信 | 已完成（手动补推）|
