import urllib.request
import json

webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"

card = {
    "msg_type": "interactive",
    "card": {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "🌙 睡前故事 · 熄屏连播彻底修复"
            },
            "template": "indigo"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "宝贝的睡前故事完成了关键修复 ✨\n\n**本次修复：**\n- 彻底解决手机熄屏后下一章不自动播放的问题\n- 采用全新播放机制：音频加载完成后自动触发播放，不依赖屏幕状态\n- 无论熄屏、锁屏、切后台，故事都会一章一章自动接续播放\n\n现在放心关屏睡觉吧，故事会一直陪着宝贝到最后一章 🎵💫"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "🌙 开始听故事"
                        },
                        "type": "primary",
                        "url": "https://zhengcls.github.io/bedtime-story/"
                    }
                ]
            }
        ]
    }
}

data = json.dumps(card).encode("utf-8")
req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=10) as resp:
    result = json.loads(resp.read().decode("utf-8"))
    print("result:", result)
    if result.get("code") == 0 or result.get("StatusCode") == 0:
        print("推送成功！")
    else:
        print("推送返回:", result)
