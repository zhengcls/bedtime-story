import urllib.request
import json

webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/f7b32472-16fb-40c1-8860-fec21f13db66"

msg = {
    "msg_type": "interactive",
    "card": {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "睡前故事 · 终极修复上线"},
            "template": "green"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**小狐狸橙橙的月亮信** 已完成重大技术升级：\n\n**本次修复内容**\n将全部 7 章节音频合并为一个完整文件，从根本上解决了微信息屏后不自动播放下一章节的问题。\n\n**为什么这次能彻底解决？**\n之前的方案需要在章节结束后切换音频文件，而微信/X5内核在息屏状态下会冻结网络请求，导致新音频无法加载。现在改为单个音频文件从头播到尾，章节之间只是时间跳转，息屏完全不影响播放。\n\n**现在的体验**\n点击「开始」后，合上手机，故事会安静地一章接一章播放到结束，无需任何操作。"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "点击收听故事"},
                        "type": "primary",
                        "url": "https://zhengcls.github.io/bedtime-story/"
                    }
                ]
            }
        ]
    }
}

data = json.dumps(msg).encode("utf-8")
req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    print("StatusCode:", resp.status)
    print(resp.read().decode("utf-8"))
