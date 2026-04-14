import urllib.request, json

webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"
story_title = "小青虫悠悠的茧中梦境"
story_desc = "小青虫悠悠在安静的茧里做了一个又一个彩色的梦，终于在某天清晨长出了美丽的翅膀"
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
