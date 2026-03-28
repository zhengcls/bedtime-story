import subprocess, json

N = 8
timestamps = []
t = 0.0
for i in range(1, N+1):
    r = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', 'audio/ch%d.mp3' % i], capture_output=True, text=True)
    d = json.loads(r.stdout)['streams'][0]['duration']
    timestamps.append((round(t, 3), round(t + float(d), 3)))
    print('ch%d: %.3fs (start=%.3f, end=%.3f)' % (i, float(d), round(t, 3), round(t + float(d), 3)))
    t += float(d)

print('Total: %.1fs' % t)
print('All timestamps:', timestamps)

# write concat list
with open('audio/concat_list.txt', 'w') as f:
    for i in range(1, N+1):
        f.write("file 'audio/ch%d.mp3'\n" % i)

# merge
r2 = subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'audio/concat_list.txt', '-acodec', 'copy', 'audio/full.mp3'], capture_output=True, text=True)
if r2.returncode != 0:
    print('merge error:', str(r2.stderr)[-300:])
else:
    r3 = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', 'audio/full.mp3'], capture_output=True, text=True)
    dur = json.loads(r3.stdout)['streams'][0]['duration']
    print('full.mp3 merged: %.3fs' % float(dur))
