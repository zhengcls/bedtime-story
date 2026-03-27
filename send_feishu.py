import urllib.request, json, ssl

url = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"
story_url = "https://zhengcls.github.io/bedtime-story/"

payload = json.dumps({
    "msg_type": "interactive",
    "card": {
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**今日睡前故事**\n《小海龟豆豆的寻星之旅》\n共7章，温馨陪伴宝贝入眠~\n\n小海龟豆豆喜欢在沙滩上数星星，一天晚上一颗流星落在了珊瑚礁旁，豆豆决定游去寻找。路上遇到了发光水母球球，一起穿过珊瑚森林，最终找到了会发光的夜明珠，像开了一场海底灯会。\n\n[点击收听](https://zhengcls.github.io/bedtime-story/)"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "开始听故事"},
                        "type": "primary",
                        "url": story_url
                    }
                ]
            }
        ],
        "header": {
            "title": {"tag": "plain_text", "content": "睡前故事来啦"},
            "template": "purple"
        }
    }
}, ensure_ascii=False).encode("utf-8")

req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
ctx = ssl.create_default_context()
resp = urllib.request.urlopen(req, context=ctx, timeout=10)
result = resp.read().decode("utf-8")
print("飞书推送结果:", result)
