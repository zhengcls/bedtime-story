import subprocess, json

# write concat list
with open('audio/concat_list.txt', 'w') as f:
    for i in range(1, 9):
        f.write("file 'audio/ch%d.mp3'\n" % i)

# merge
r2 = subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'audio/concat_list.txt', '-acodec', 'copy', 'audio/full.mp3'], capture_output=True, text=True)
print('returncode:', r2.returncode)
if r2.returncode != 0:
    err = str(r2.stderr)
    print('error:', err[-300:])

# verify
r3 = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', 'audio/full.mp3'], capture_output=True, text=True)
dur = float(json.loads(r3.stdout)['streams'][0]['duration'])
print('full.mp3 duration:', dur, 's')

# hash check
import hashlib
with open('audio/full.mp3', 'rb') as fp:
    print('full.mp3 md5:', hashlib.md5(fp.read()).hexdigest())
