# 项目记忆 - 睡前故事推送

## 睡前故事生成标准流程
1. 生成故事内容：AI生成温馨儿童睡前故事，6~7个章节，每章50~80字
2. 生成音频：用 Edge TTS (zh-CN-XiaoyiNeural) 为每章生成MP3，存放到 audio/ 目录
3. 编写 index.html：基于现有模板替换故事数据（Unicode编码），严格遵循微信兼容规范
4. 本地测试：用 preview_url 预览验证
5. 部署到 GitHub Pages：git push origin main
6. 验证线上：确认HTML和音频文件正常
7. 推送飞书群：通过飞书 Webhook 发送故事卡片到群聊

## 用户偏好
- **自动化任务全自动执行**：定时任务中遇到任何需要做选择的情况，自动选择并继续执行，不需要询问用户确认

## 关键信息
- 线上地址：https://zhengcls.github.io/bedtime-story/
- 音频路径：audio/ch1.mp3 ~ ch7.mp3
- TTS 语音：zh-CN-XiaoyiNeural
- 定时任务：每天 21:45 自动执行
- HTML 中故事文本需 Unicode 编码
- 微信兼容：preload="none" playsinline webkit-playsinline
- 飞书 Webhook：https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66

## 故事历史
| 日期 | 故事名 | 状态 |
|------|--------|------|
| 2026-03-27 | 小萤火虫亮亮的星光梦 | 已完成 |
| 2026-03-27 | 小松鼠果果的彩虹桥 | 已完成 |
| 2026-03-27 | 小海龟豆豆的寻星之旅 | 已完成 |

## 优化经验
- **飞书推送卡顿根因**：PowerShell 的 curl 是 Invoke-WebRequest 的别名，处理 JSON 中的 URL/特殊字符会反复失败。**改用 Python send_feishu.py 脚本发送**，一次成功，避免浪费 5-10 分钟重试
- **TTS 生成**：Node.js tts-converter.js 处理含引号的中文文本会失败，改用 Python edge-tts 库（通过脚本文件调用）更稳定
- **优化建议**：将飞书推送和 TTS 生成都统一用 Python 脚本，减少 PowerShell 转义问题
