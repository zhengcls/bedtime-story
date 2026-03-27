import asyncio, edge_tts, sys

async def gen(text, out, ch):
    comm = edge_tts.Communicate(text, "zh-CN-XiaoyiNeural", rate="-10%")
    await comm.save(out)
    print(f"Ch{ch} done: {out}")

texts = {
    3: "游啊游，豆豆遇到了一只发光的水母。水母名叫球球，浑身散发着蓝色的柔光。球球好奇地问豆豆：你要去哪里呀？豆豆说：我要去找落在海里的星星！球球想了想说：我陪你去吧，我的光可以帮你照亮路。",
    4: "他们一起穿过了一片美丽的珊瑚森林。红色的珊瑚像小树，紫色的海葵像花朵，还有好多小鱼在中间游来游去。一只小丑鱼探出头来问：你们在找什么呢？豆豆说：在找一颗从天上掉下来的星星。",
    6: "豆豆轻轻用小鳍碰了碰夜明珠，它突然亮了好多倍，整个海底都被照得金灿灿的。海马、小螃蟹、海星都跑过来看热闹。大家围坐在一起，像开了一场海底的灯会。",
    7: "豆豆抱着夜明珠慢慢游回了家。他把夜明珠放在沙滩上的小窝旁，整个夜晚都亮堂堂的。海浪轻轻拍着沙滩，像在唱一首温柔的摇篮曲。豆豆缩进壳里，甜甜地睡着了。晚安，小海龟。晚安，全世界。"
}

async def main():
    for ch, text in texts.items():
        out = r"f:\龙虾机器人\日常定时推送\bedtime-story\audio\ch" + str(ch) + ".mp3"
        await gen(text, out, ch)
    print("All chapters generated!")

asyncio.run(main())
