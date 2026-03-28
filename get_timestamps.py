import subprocess, json

N = 8
timestamps = []
t = 0
for i in range(1, N + 1):
    r = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', f'audio/ch{i}.mp3'],
        capture_output=True, text=True
    )
    duration = float(json.loads(r.stdout)['streams'][0]['duration'])
    timestamps.append((round(t, 3), round(t + duration, 3)))
    t += duration

print("chapters timestamps:")
for i, (s, e) in enumerate(timestamps):
    print(f"  ch{i+1}: start={s}, end={e}")
