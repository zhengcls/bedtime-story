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
                "content": "🌙 睡前故事 · 体验升级"
            },
            "template": "purple"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "宝贝的睡前故事已完成优化升级 ✨\n\n**本次更新：**\n- 界面更简洁，去掉了章节按钮干扰\n- 修复熄屏后自动翻章不播放的问题\n\n现在可以放心把手机屏幕关掉，故事会一章一章自动接着播，直到讲完为止 🎵\n\n点击下方按钮，让宝贝安心入睡吧 💫"
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
    print("飞书推送结果:", result)
    if result.get("code") == 0 or result.get("StatusCode") == 0:
        print("推送成功！")
    else:
        print("推送返回:", result)
