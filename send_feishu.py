import urllib.request, json, re, os

PROJECT = r"f:\龙虾机器人\日常定时推送\bedtime-story"
WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"
URL = "https://zhengcls.github.io/bedtime-story/"

def get_story_info_from_html():
    """从 index.html 自动提取故事标题和描述"""
    html_path = os.path.join(PROJECT, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取标题（<title>标签）
    title_m = re.search(r"<title>(.*?)</title>", content)
    story_title = title_m.group(1) if title_m else "睡前故事"

    # 提取第一章文本作为描述（取前60字）
    ch_m = re.search(r'"text"\s*:\s*"([^"]{10,})"', content, re.DOTALL)
    if ch_m:
        text = ch_m.group(1)[:60].replace('\\n', '').replace('\\', '')
        story_desc = text + "..."
    else:
        story_desc = "温馨的睡前故事"

    return story_title, story_desc

story_title, story_desc = get_story_info_from_html()
print(f"自动提取: title={story_title}, desc={story_desc}")

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
                 "type": "primary", "url": URL}
            ]}
        ]
    }
}

data = json.dumps(card, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(WEBHOOK, data=data, headers={'Content-Type': 'application/json; charset=utf-8'})
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode('utf-8'))
