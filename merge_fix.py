import subprocess, json

# 检查各章节实际时长
t = 0.0
timestamps = []
for i in range(1, 9):
    r = subprocess.run(['ffprobe','-v','quiet','-print_format','json','-show_streams',f'audio/ch{i}.mp3'], capture_output=True, text=True)
    d = float(json.loads(r.stdout)['streams'][0]['duration'])
    timestamps.append((round(t, 3), round(t + d, 3)))
    print(f'ch{i}: {d}s, start={round(t,3)}, end={round(t+d,3)}')
    t += d
print(f'Total: {round(t, 1)}s')
print(f'timestamps = {timestamps}')

# 写 concat 文件
with open('audio/concat_list.txt', 'w', encoding='utf-8') as f:
    for i in range(1, 9):
        f.write(f"file 'audio/ch{i}.mp3'\n")
print('concat_list.txt written')

# 合并
r2 = subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'audio/concat_list.txt', '-acodec', 'copy', 'audio/full.mp3'], capture_output=True, text=True)
if r2.returncode != 0:
    print(f'ffmpeg error: {r2.stderr[-500:]}')
else:
    print('merge success')

# 验证
r3 = subprocess.run(['ffprobe','-v','quiet','-print_format','json','-show_streams','audio/full.mp3'], capture_output=True, text=True)
print(f'full.mp3 duration: {json.loads(r3.stdout)["streams"][0]["duration"]}s')
