import asyncio
import edge_tts

chapters = [
    (1, "小狐狸橙橙住在橘子林里，每天晚上都要给月亮写一封信，把今天开心的事情说给月亮听。"),
    (2, "今晚，橙橙用树叶折了一艘小船，把信放进去，轻轻地放到了小溪里，说：月亮姐姐，帮我把信带上去吧。"),
    (3, "小溪咕噜咕噜地答应了，载着信慢慢漂远。夜莺在树上唱起了歌，好像在为那封信伴奏，美妙极了。"),
    (4, "月亮听到了歌声，弯弯地笑了，把银色的光铺满整片橘子林。橙橙坐在树根旁，感觉整个世界都温暖亮堂堂的。"),
    (5, "好朋友小松鼠跑来了，毛茸茸的尾巴摇啊摇，说：我也想给月亮写信！两个小伙伴一起折了好多树叶小船，放进小溪里。"),
    (6, "小溪载着满满的信漂向远方，月亮越来越圆，光芒也越来越柔和，把睡意轻轻洒进森林的每一个角落。"),
    (7, "橙橙趴在松软的落叶堆里，望着月亮，心里暖暖的。她轻轻闭上眼睛，嘴角带着微笑睡着了。月亮守护着她，直到天亮。晚安，好梦，小朋友。"),
]

async def gen():
    for idx, text in chapters:
        output = f"audio/ch{idx}.mp3"
        communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoyiNeural", rate="-10%")
        await communicate.save(output)
        print(f"生成完成: {output}")

asyncio.run(gen())
print("所有音频生成完毕！")
