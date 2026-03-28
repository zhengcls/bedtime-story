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
                "content": "🦊 小狐狸橙橙的月亮信"
            },
            "template": "indigo"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "宝贝，晚上好！今天的睡前故事来啦 ✨\n\n小狐狸橙橙每天晚上都要给月亮写一封信，用树叶折成小船放进小溪，让小溪把信带给月亮姐姐。月亮听到后，弯弯地笑了，把银色的光铺满了整片橘子林……欢迎和宝贝一起来听这个温馨的故事！\n\n📚 **共 7 章** | 🎧 可爱小动物主角 | ✨ 香甜入梦"
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
