# 项目记忆 - 睡前故事推送

## 睡前故事生成完整标准流程（全自动执行）

### 第1步：生成故事内容
- 生成温馨儿童睡前故事，6~7个章节
- 每章50~80字，内容适合睡前聆听
- 主角为可爱小动物，情节温馨治愈
- 输出格式：JSON数组，包含 title/text/url 字段

### 第2步：生成音频（Python edge-tts）
- 使用 Python edge-tts 库生成，**禁止在命令行直接拼接中文文本**
- 语音：zh-CN-XiaoyiNeural（女声温柔）
- 格式：MP3，存放到 audio/ch1.mp3 ~ ch7.mp3
- 代码模式：通过脚本文件调用，避免 PowerShell 转义问题

### 第3步：编写 index.html
- 基于当前模板（深色渐变背景 + 开始遮罩层 + 原生audio控件）
- 故事数据嵌入 JS 的 chapters 数组
- **章节按钮文字用 Unicode 编码**：`\u7B2C` + 数字 + `\u7AE0`
- 微信兼容：`preload="none" playsinline webkit-playsinline`
- 功能：开始遮罩层、章节导航、自动连播开关、上一章/下一章

### 第4步：本地预览验证
- 使用 preview_url 工具预览页面
- 验证：开始按钮、音频播放、章节切换、自动连播

### 第5步：部署到 GitHub Pages
```bash
git add -A
git commit -m "feat: 新增睡前故事《故事名》"
git push origin main
```

### 第6步：验证线上
- 访问 https://zhengcls.github.io/bedtime-story/
- 确认 HTML 和音频文件都能正常加载

### 第7步：推送飞书群（Python脚本）
- **必须使用 Python send_feishu.py 脚本**，禁止用 curl
- Webhook：https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66
- 卡片内容：故事标题 + 简介 + 链接按钮
- 执行：`python send_feishu.py`

---

## 用户偏好
- **自动化任务全自动执行**：定时任务中遇到任何需要做选择的情况，自动选择并继续执行，不需要询问用户确认

## 定时任务配置
- **任务ID**: automation
- **执行时间**: 每天 21:45
- **状态**: ACTIVE
- **工作目录**: f:\龙虾机器人\日常定时推送\bedtime-story

## 关键信息
- 线上地址：https://zhengcls.github.io/bedtime-story/
- 音频路径：audio/ch1.mp3 ~ ch7.mp3
- TTS 语音：zh-CN-XiaoyiNeural
- 定时任务：每天 21:45 自动执行
- 飞书 Webhook：https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66

## 核心技术规范

### 必须遵守（避免卡顿）
1. **TTS生成**：用 Python edge-tts 库，写脚本文件执行，禁止命令行拼接中文
2. **飞书推送**：用 send_feishu.py 脚本，禁止用 PowerShell curl
3. **HTML编码**：HTML 标签内容直接写中文；JS 字符串中可选择 Unicode 或直接中文均可，但统一用直接中文更安全
4. **Git操作**：中文路径偶尔出问题，失败时重试一次

### HTML播放器功能清单
- [ ] 开始遮罩层（金色脉冲按钮）
- [ ] 原生 audio 控件（controls）
- [ ] 章节导航按钮组（第1章~第7章）
- [ ] 当前章节高亮
- [ ] 上一章/下一章按钮
- [ ] 自动连播开关（默认开启）
- [ ] 音频结束自动跳转下一章
- [ ] 微信兼容属性

## 故事历史
| 日期 | 故事名 | 状态 |
|------|--------|------|
| 2026-03-27 | 小萤火虫亮亮的星光梦 | 已完成 |
| 2026-03-27 | 小松鼠果果的彩虹桥 | 已完成 |
| 2026-03-27 | 小海龟豆豆的寻星之旅 | 已完成 |
| 2026-03-28 | 小乌龟慢慢的星星花园 | 已完成 |

## 踩坑经验
- **PowerShell curl 陷阱**：PowerShell 的 curl 是 Invoke-WebRequest 的别名，处理 JSON 中的 URL/特殊字符会反复失败，浪费 5-10 分钟
- **TTS 中文引号问题**：命令行传递含引号的中文会解析失败，必须用脚本文件
- **⚠️ Unicode 编码仅限 JS！HTML 标签内容禁用**：`\u5c0f` 等 Unicode 转义**只在 JavaScript 字符串中有效**，放在 HTML 标签内容（如 `<title>`、`<div>` 文本节点）中会直接显示原始转义字符串，导致乱码。HTML 部分必须直接写中文，JS 字符串中可以用 Unicode 转义也可以直接写中文。
