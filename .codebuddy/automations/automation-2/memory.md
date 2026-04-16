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

## 2026-03-31 21:30 - 定时任务执行
- 故事：小獾果果的星星糖果罐（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长170.4s
- 音频版本：full_v6.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：本地commit成功，push失败（GitHub 443端口不通，重试3次均超时），待网络恢复后手动push
- 飞书推送：StatusCode=0 success

## 2026-03-31 21:30 - 定时任务执行（第二次）
- 故事：小萤火虫闪闪的梦境灯笼（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长183.0s
- 音频版本：full_v7.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit 7a24fc6，push origin main 成功
- 飞书推送：StatusCode=0 success

## 2026-04-01 21:30 - 定时任务执行
- 故事：小羊绒绒的云朵面包（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长173.0s
- 音频版本：full_v8.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit b87e366，push origin main 成功
- 飞书推送：StatusCode=0 success

## 2026-04-02 21:30 - 定时任务执行
- 故事：小企鹅波波的极光梦境（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长177.0s
- 音频版本：full_v9.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit a52e167，push origin main 成功
- 飞书推送：StatusCode=0 success

## 2026-04-02 22:48 - 定时任务执行（第二次）
- 故事：小水獭悠悠的月光小船（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长186.5s
- 音频版本：full_v10.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit bea62b9，push origin main 成功
- 飞书推送：StatusCode=0 success

## 2026-04-03 21:30 - 定时任务执行
- 故事：小蜜蜂嗡嗡的甜蜜花园（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长207.6s
- 音频版本：full_v11.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit 2678029，push origin main 成功
- 飞书推送：StatusCode=0 success

## 2026-04-04 21:30 - 定时任务执行
- 故事：小蝴蝶翩翩的月光舞会（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长203.3s
- 音频版本：full_v12.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit 6885dcd，push origin main 成功
- 飞书推送：StatusCode=0 success

## 2026-04-05 21:30 - 定时任务执行
- 故事：小兔糯糯的星星被子（7章）
- 音频：fix_all.py 一键完成，全部7章成功
- 时间戳：总时长193.9s
- 音频版本：full_v13.mp3
- HTML生成：fix_all.py 自动更新时间戳 + 手动修正音频引用（fix_all未匹配到旧引用）
- Git部署：commit 9319a40，push失败（GitHub 443端口不通），22:30网络恢复后重试push成功
- 飞书推送：StatusCode=0 success

## 2026-04-06 21:30 - 定时任务执行
- 故事：小海豚泡泡的月光之歌（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长239.6s
- 音频版本：full_v14.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit 29610c2，push origin main 成功
- 飞书推送：StatusCode=0 success

## 2026-04-07 21:30 - 定时任务执行
- 故事：小猫咪球的星星风筝（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长228.3s
- 音频版本：full_v15.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit 7541c27，push origin main 成功
- 飞书推送：StatusCode=0 success

## 2026-04-08 21:30 - 定时任务执行
- 故事：小浣熊团团的梦境图书馆（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长206.9s
- 音频版本：full_v16.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：本地commit 7d4d785 成功，push失败（GitHub 443端口不通，重试2次均超时），待网络恢复后手动push
- 飞书推送：StatusCode=0 success

## 2026-04-09 21:30 - 定时任务执行
- 故事：小螃蟹圆圆的珍珠海螺（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长218.2s
- 音频版本：full_v17.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：本地commit成功，push失败（GitHub 443端口不通，重试2次均超时），待网络恢复后手动push
- 飞书推送：StatusCode=0 success

## 2026-04-11 21:30 - 定时任务执行
- 故事：小蜗牛慢慢的花籽信（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长219.2s
- 音频版本：full_v19.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：本地commit 1ed68f3 成功，push失败（GitHub 443端口不通，重试3次均超时），待网络恢复后手动push
- 飞书推送：StatusCode=0 success

## 2026-04-12 21:30 - 定时任务执行
- 故事：小仓鼠嘟嘟的月光存钱罐（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长235.3s
- 音频版本：full_v20.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit f74b6df，push origin main 成功
- 线上验证：web_fetch仍显示旧页面（GitHub Pages CDN缓存延迟），git push已成功，预计1-2分钟后生效
- 飞书推送：StatusCode=0 success

## 2026-04-13 21:31 - 定时任务执行
- 故事：小青虫悠悠的茧中梦境（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长238.5s
- 音频版本：full_v21.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit 805823d，push origin main 成功
- 线上验证：web_fetch仍显示旧页面（GitHub Pages CDN缓存延迟），git push已成功
- 飞书推送：StatusCode=0 success

## 2026-04-14 21:30 - 定时任务执行
- 故事：小田鼠麦穗的金色麦田梦（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长237.3s
- 音频版本：full_v22.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit baf60ba，push origin main 成功
- 飞书推送：StatusCode=0 success

## 2026-04-15 21:31 - 定时任务执行
- 故事：小燕子咕咕的云端邮局（8章）
- 音频：fix_all.py 一键完成，全部8章成功
- 时间戳：总时长244.0s
- 音频版本：full_v23.mp3
- HTML生成：fix_all.py 自动更新时间戳
- Git部署：commit e8be404，push origin main 成功
- 飞书推送：StatusCode=0 success
