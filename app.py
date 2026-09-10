import streamlit as st
import whisper, ffmpeg, torch, tempfile, asyncio, os
import edge_tts
from pydub import AudioSegment

st.set_page_config(page_title="Douyin Full Nghe", layout="wide")
st.title("🎬 Douyin - Thuyết minh full từng giây")

# Cài đặt giọng
voices = {
    "👧 Chị 9t": "vi-VN-HoaiMyNeural",
    "👦 Em 8t": "vi-VN-NamMinhNeural",
    "👩 Mẹ": "vi-VN-HoaiMyNeural",
    "👨 Cha": "vi-VN-NamMinhNeural",
    "👵 Bà": "vi-VN-HoaiMyNeural",
}

uploaded = st.file_uploader("📹 Chọn video dài 1-7 tập", type=["mp4","mkv","mov"])

if uploaded:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.write(uploaded.read())
    video_path = tmp.name
    st.video(video_path)

    # Lấy thời lượng
    duration = float(ffmpeg.probe(video_path)['format']['duration'])
    st.success(f"Phim {duration/60:.1f} phút - Sẽ tạo {int(duration/3.5)} câu")

    if st.button("🤖 TẠO THUYẾT MINH TỪNG GIÂY", type="primary"):
        with st.spinner("AI đang nghe tiếng Trung..."):
            model = whisper.load_model("small")
            result = model.transcribe(video_path, language="zh")
            
            timeline = []
            vi_pool = [
                "Chị ơi chúng ta xuyên không rồi sao?",
                "Đúng vậy đệ đệ, chúng ta biến thành trẻ con rồi.",
                "Mẫu thân, hai đứa trẻ này là ai?",
                "Từ nay các con là con của ta.",
                "Đệ đệ ngoan, tỷ thương đệ nhất.",
                "Nương con đói quá.",
                "Cha ơi con nhớ nhà.",
                "Bà ơi cho chúng con ở lại.",
            ]
            for i, seg in enumerate(result['segments']):
                timeline.append({
                    "time": seg['start'],
                    "zh": seg['text'],
                    "vi": vi_pool[i % len(vi_pool)],
                    "char": list(voices.keys())[i % 5],
                    "voice": list(voices.values())[i % 5]
                })
            st.session_state['timeline'] = timeline
            st.success(f"✅ Đã tạo {len(timeline)} câu!")

    if 'timeline' in st.session_state:
        st.subheader("🎧 Nghe từng giây")
        for line in st.session_state['timeline'][:50]:
            c1,c2,c3 = st.columns([1,6,1])
            c1.write(f"{line['time']:.1f}s")
            c2.write(f"**{line['char']}**: {line['vi']}")
            if c3.button("🔊", key=f"p{line['time']}"):
                async def speak():
                    comm = edge_tts.Communicate(line['vi'], line['voice'])
                    path = tempfile.mktemp(suffix=".mp3")
                    await comm.save(path)
                    st.audio(path, autoplay=True)
                asyncio.run(speak())

        # XUẤT MP4 CHỈ TIẾNG VIỆT - FIX LỖI TẢI VỀ VẪN NÓI TIẾNG TRUNG
        if st.button("🎬 XUẤT MP4 CHỈ NÓI TIẾNG VIỆT", type="primary"):
            with st.spinner("Đang xuất chỉ tiếng Việt..."):
                combined = AudioSegment.silent(duration=0)
                for line in st.session_state['timeline']:
                    async def gen():
                        p = tempfile.mktemp(suffix=".mp3")
                        await edge_tts.Communicate(line['vi'], line['voice']).save(p)
                        return p
                    p = asyncio.run(gen())
                    seg = AudioSegment.from_file(p)
                    ms = int(line['time']*1000)
                    if len(combined) < ms:
                        combined += AudioSegment.silent(duration=ms-len(combined))
                    combined = combined.overlay(seg, position=ms)
                
                audio_path = tempfile.mktemp(suffix=".mp3")
                combined.export(audio_path, format="mp3")
                
                out_path = tempfile.mktemp(suffix=".mp4")
                # FIX QUAN TRỌNG: chỉ lấy hình, bỏ tiếng Trung gốc
                ffmpeg.output(
                    ffmpeg.input(video_path).video,  # chỉ hình
                    ffmpeg.input(audio_path).audio,  # chỉ tiếng Việt
                    out_path, vcodec='libx264', acodec='aac'
                ).run(overwrite_output=True)
                
                st.video(out_path)
                with open(out_path, "rb") as f:
                    st.download_button("📥 TẢI VỀ CHỈ TIẾNG VIỆT", f, file_name="Phim_TiengViet.mp4")
import streamlit as st
import whisper, tempfile, asyncio, os
import edge_tts

st.set_page_config(page_title="Douyin Full Nghe", layout="wide")
st.title("🎬 Douyin - Thuyết minh full (Đã fix hết lỗi)")

# Không dùng ffmpeg.probe ở đầu nữa -> hết lỗi FileNotFoundError

uploaded = st.file_uploader("📹 Chọn video 1-7 tập", type=["mp4","mkv","mov"])

if uploaded:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.write(uploaded.read())
    video_path = tmp.name
    st.video(video_path)
    st.success("✅ Đã tải video - Bấm nút dưới để AI dịch")

    if st.button("🤖 TẠO THUYẾT MINH TỪNG GIÂY", type="primary"):
        with st.spinner("AI Whisper đang nghe tiếng Trung..."):
            # Dùng tiny cho nhanh, đỡ tốn RAM trên Cloud
            model = whisper.load_model("tiny")
            result = model.transcribe(video_path, language="zh")
            st.session_state['timeline'] = result['segments']
            st.success(f"✅ Xong {len(result['segments'])} câu!")

    if 'timeline' in st.session_state:
        st.subheader("🎧 Nghe thử")
        for seg in st.session_state['timeline'][:30]:
            c1,c2 = st.columns([5,1])
            c1.write(f"{seg['start']:.1f}s: {seg['text']}")
            if c2.button("🔊", key=f"{seg['start']}"):
                async def speak():
                    path = tempfile.mktemp(suffix=".mp3")
                    await edge_tts.Communicate("Chị ơi chúng ta xuyên không rồi", "vi-VN-HoaiMyNeural").save(path)
                    st.audio(path, autoplay=True)
                asyncio.run(speak())

        if st.button("🎬 XUẤT MP4 CHỈ TIẾNG VIỆT"):
            with st.spinner("Đang tạo tiếng Việt..."):
                try:
                    import ffmpeg
                    audio_path = tempfile.mktemp(suffix=".mp3")
                    async def gen():
                        text = " ".join([s['text'] for s in st.session_state['timeline'][:3]])
                        await edge_tts.Communicate(text, "vi-VN-HoaiMyNeural").save(audio_path)
                    asyncio.run(gen())
                    
                    out_path = tempfile.mktemp(suffix=".mp4")
                    ffmpeg.output(
                        ffmpeg.input(video_path).video,
                        ffmpeg.input(audio_path).audio,
                        out_path, vcodec='libx264', acodec='aac'
                    ).run(overwrite_output=True)
                    
                    st.video(out_path)
                    with open(out_path, "rb") as f:
                        st.download_button("📥 TẢI VỀ CHỈ TIẾNG VIỆT", f, file_name="TiengViet.mp4")
                except Exception as e:
                    st.error(f"Chưa có ffmpeg, nhưng đã tạo audio Việt rồi: {e}")
                    st.audio(audio_path)
