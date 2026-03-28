import subprocess, json, os, hashlib

os.chdir('f:/龙虾机器人/日常定时推送/bedtime-story')

# verify ch1.mp3 is new
r0 = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', 'audio/ch1.mp3'], capture_output=True, text=True)
ch1_dur = float(json.loads(r0.stdout)['streams'][0]['duration'])
print('ch1.mp3 duration:', ch1_dur, 's (should be ~16-17s for new content)')

# write concat list with RELATIVE paths (no audio/ prefix!)
with open('audio/concat_list.txt', 'w') as f:
    for i in range(1, 9):
        f.write("file 'ch%d.mp3'\n" % i)

print('concat_list.txt written')
print(open('audio/concat_list.txt').read())

# merge from WITHIN audio directory
r2 = subprocess.run(
    ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat_list.txt', '-acodec', 'copy', '../full.mp3'],
    cwd='f:/龙虾机器人/日常定时推送/bedtime-story/audio',
    capture_output=True, text=True
)
print('ffmpeg returncode:', r2.returncode)
if r2.returncode != 0:
    print('error:', str(r2.stderr)[-300:])

# verify
r3 = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', 'audio/full.mp3'], capture_output=True, text=True)
dur = float(json.loads(r3.stdout)['streams'][0]['duration'])
print('full.mp3 duration:', dur, 's')

with open('audio/full.mp3', 'rb') as fp:
    print('full.mp3 md5:', hashlib.md5(fp.read()).hexdigest())
