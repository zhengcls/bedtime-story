# 每日睡前故事推送 - 执行记录

## 2026-03-27 (第三次) 22:52 - 23:02
- 故事：小海龟豆豆的寻星之旅（7章）
- 音频：Edge TTS zh-CN-XiaoyiNeural rate=-10%，全部7章成功
- 部署：commit 373c406，push origin main 成功
- 线上验证：HTML和音频正常
- 飞书推送：Python脚本发送，StatusCode=0 success
- 问题：PowerShell curl 转义导致飞书推送卡顿约8分钟，已优化为Python脚本方案

## 优化措施
1. 保留 send_feishu.py 用于后续飞书推送（避免 PowerShell 转义）
2. TTS 优先用 Python edge-tts 库（对中文引号更稳定）
3. 整体流程可缩短至约3分钟

## 2026-03-28 12:02 - 流水线优化版首次执行
- 故事：小猫妙妙的月亮船（8章）
- 音频：Edge TTS 并行生成（并发数4），全部8章成功，耗时6.0s
- 时间戳：总时长120.5s
- HTML生成：成功
- Git部署：成功
- 飞书推送：StatusCode=0 success
- 总耗时：15.5s（优化版流水线效果显著）

## 2026-03-28 21:47 - 第二次定时任务执行（额外）
- 故事：小狐狸暖暖的彩虹桥（8章）
- 音频：Edge TTS zh-CN-XiaoyiNeural，全部8章成功
- 时间戳：总时长116.3s
- 音频版本：full_v3.mp3
- HTML生成：成功
- Git部署：commit 24aaddb，push origin main 成功
- 飞书推送：StatusCode=0 success
- 注意：fix_all.py get_chapters_from_html 要求 chapters 数组属性名用双引号（合法 JSON）

## 2026-03-28 21:30 - 定时任务执行
- 故事：小鹿斑斑的梦境花园（8章）
- 音频：Edge TTS 并行生成（并发数4），全部8章成功，耗时5.7s
- 时间戳：总时长124.5s
- HTML生成：成功
- Git部署：成功
- 飞书推送：StatusCode=0 success
- 总耗时：12.3s

## 2026-03-28 21:30 - 定时任务执行（第二次，覆盖）
- 故事：小刺猬圆圆的星光灯笼（8章）
- 音频：Edge TTS zh-CN-XiaoyiNeural，全部8章成功
- 时间戳：总时长118.0s
- 音频版本：full_v4.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：本地commit成功，push失败（GitHub 443端口不通，重试5次均超时），待网络恢复后手动push
- 飞书推送：StatusCode=0 success
- 补充：22:09 网络恢复后重试，commit 1ba6f0a push 成功，任务完成

## 2026-03-28 22:16 - 定时任务执行
- 故事：小松鼠栗栗的许愿风铃（8章）
- 音频：Edge TTS zh-CN-XiaoyiNeural，全部8章成功
- 时间戳：总时长132.3s
- 音频版本：full_v5.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit 2a158a7，push origin main 成功
- 飞书推送：StatusCode=0 success
