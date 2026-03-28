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
                "content": "\U0001f422 \u5c0f\u4e4c\u9f9f\u6162\u6162\u7684\u661f\u661f\u82b1\u56ed"
            },
            "template": "indigo"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "\u5b9d\u8d1d\uff0c\u665a\u4e0a\u597d\uff01\u4eca\u5929\u7684\u7761\u524d\u6545\u4e8b\u6765\u554a \u2728\n\n\u5c0f\u4e4c\u9f9f\u6162\u6162\u6709\u4e00\u4e2a\u68a6\u60f3\uff0c\u8981\u79cd\u4e00\u7247\u4f1a\u53d1\u5149\u7684\u661f\u661f\u82b1\u3002\u5728\u5c0f\u8681\u8549\u548c\u5c0f\u871c\u8702\u7684\u5e2e\u52a9\u4e0b\uff0c\u5979\u7684\u68a6\u60f3\u5b9e\u73b0\u4e86\u2014\u2014\u82b1\u56ed\u91cc\u5f00\u6ee1\u4e86\u4f1a\u53d1\u5149\u7684\u661f\u661f\u82b1\u3002\u6b3e\u8fce\u548c\u5b9d\u8d1d\u4e00\u8d77\u6765\u542c\u8fd9\u4e2a\u6e29\u99a8\u7684\u6545\u4e8b\uff01\n\n\U0001f4da **\u5171 7 \u7ae0** | \U0001f3a7 \u91cd\u5c0f\u52a8\u7269\u4e3b\u89d2 | \u2728 \u9999\u751c\u5165\u68a6"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "\U0001f319 \u5f00\u59cb\u542c\u6545\u4e8b"
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
