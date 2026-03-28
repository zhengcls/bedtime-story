import urllib.request
url = "https://zhengcls.github.io/story-player/player.html"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode("utf-8")
with open(r"f:\龙虾机器人\日常定时推送\bedtime-story\temp_source.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved {len(html)} chars")
