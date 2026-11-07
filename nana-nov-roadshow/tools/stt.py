import sys, json, glob, os, numpy as np, soundfile as sf, sherpa_onnx
S=sys.argv[1]; M=S+"/models"; W=M+"/sherpa-onnx-whisper-large-v3/large-v3-"
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=W+"encoder.int8.onnx",decoder=W+"decoder.int8.onnx",tokens=W+"tokens.txt",language="ja",task="transcribe",num_threads=4)
cfg=sherpa_onnx.VadModelConfig(); cfg.silero_vad.model=M+"/silero_vad.onnx"; cfg.silero_vad.min_silence_duration=0.35; cfg.silero_vad.min_speech_duration=0.25; cfg.silero_vad.threshold=0.5; cfg.sample_rate=16000
out=[]
for f in sorted(glob.glob(S+"/audio/0*.wav")):
    a,sr=sf.read(f,dtype="float32"); vad=sherpa_onnx.VoiceActivityDetector(cfg,buffer_size_in_seconds=60)
    segs=[]
    for i in range(0,len(a),512): vad.accept_waveform(a[i:i+512])
    vad.flush()
    while not vad.empty(): segs.append((vad.front.start, np.array(vad.front.samples))); vad.pop()
    for st,smp in segs:
        s=rec.create_stream(); s.accept_waveform(16000,smp); rec.decode_stream(s)
        r={"clip":os.path.basename(f)[:2],"start":round(st/16000,2),"end":round((st+len(smp))/16000,2),"text":s.result.text.strip()}
        out.append(r); print(r,flush=True)
json.dump(out,open(S+"/segments.json","w"),ensure_ascii=False,indent=1)
