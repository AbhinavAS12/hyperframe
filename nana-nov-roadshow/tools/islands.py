import sys,json,soundfile as sf,sherpa_onnx
S=sys.argv[1]; W=S+"/models/sherpa-onnx-whisper-large-v3/large-v3-"
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=W+"encoder.int8.onnx",decoder=W+"decoder.int8.onnx",tokens=W+"tokens.txt",language="ja",task="transcribe",num_threads=4)
isl={"1":"0.22-2.02 2.27-5.25 5.34-9.86","2":"0.28-1.44 1.53-3.68 3.93-4.64 4.73-6.60 6.81-13.57","3":"0.28-1.44 1.53-4.55 4.76-8.52 8.57-11.84","4":"0.32-3.78 4.09-4.77 4.83-6.47","5":"0.28-4.4 4.4-8.61"}
out={}
for c,s in isl.items():
    a,_=sf.read(f"{S}/audio/c{c}.wav",dtype="float32"); out[c]=[]
    for r in s.split():
        st,en=map(float,r.split("-")); seg=a[int(max(0,st-0.05)*16000):int((en+0.05)*16000)]
        x=rec.create_stream(); x.accept_waveform(16000,seg); rec.decode_stream(x)
        out[c].append([st,en,x.result.text.strip()]); print(c,st,en,x.result.text.strip(),flush=True)
json.dump(out,open(S+"/islands.json","w"),ensure_ascii=False)
