
import streamlit as st
import whisper
import tempfile
import os

st.title("🎬 AI Dịch Phim Trung Quốc → Tiếng Việt")

model = whisper.load_model("small")

video = st.file_uploader("Tải video phim", type=["mp4","mkv","mov","avi"])

if video:
    st.video(video)

    if st.button("Bắt đầu dịch"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(video.read())
            video_path = f.name

        st.info("Đang nhận diện lời thoại...")

        result = model.transcribe(video_path, language="zh")

        st.success("Đã nhận diện xong!")

        st.subheader("Lời thoại tiếng Trung")
        st.write(result["text"])

        st.subheader("Bản dịch tiếng Việt")
        st.write("<< Dịch sang tiếng Việt tại đây >>")

        st.download_button(
            "Tải phụ đề tiếng Việt",
            result["text"],
            file_name="phude_tiengviet.txt"
        )
