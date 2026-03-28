import shutil, hashlib, subprocess, json, os

os.chdir('f:/龙虾机器人/日常定时推送/bedtime-story')

# 1. copy full.mp3 -> full_v2.mp3
shutil.copy('audio/full.mp3', 'audio/full_v2.mp3')
print('full_v2.mp3 created')

# 2. update index.html: replace full.mp3 with full_v2.mp3
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_new = html.replace('audio/full.mp3', 'audio/full_v2.mp3')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_new)
print('index.html updated')

# 3. verify audio
r = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', 'audio/full_v2.mp3'], capture_output=True, text=True)
dur = float(json.loads(r.stdout)['streams'][0]['duration'])
print('full_v2.mp3 duration:', dur, 's')
with open('audio/full_v2.mp3', 'rb') as f:
    print('full_v2.mp3 md5:', hashlib.md5(f.read()).hexdigest())

# 4. git add + commit + push
subprocess.run(['git', 'add', '-A'], capture_output=True)
r2 = subprocess.run(['git', 'commit', '-m', 'fix: 音频版本升级为full_v2强制刷新'], capture_output=True, text=True)
print('commit:', r2.returncode)
r3 = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
print('push returncode:', r3.returncode)
print('push stderr:', str(r3.stderr)[-200:] if r3.stderr else 'ok')
