
import streamlit as st
import os
from gtts import gTTS
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip, AudioFileClip

st.set_page_config(page_title="App Dịch & Lồng Tiếng Phim", page_icon="🎬", layout="centered")

st.title("🎬 Ứng Dụng Dịch & Lồng Tiếng Phim")
st.write("Tải video lên để dịch và tạo video lồng tiếng tự động!")

uploaded_file = st.file_uploader("Chọn tệp video (MP4, AVI, MOV)...", type=["mp4", "avi", "mov"])

target_lang = st.selectbox(
    "Chọn ngôn ngữ muốn lồng tiếng:",
    options=[("Tiếng Việt", "vi"), ("Tiếng Anh", "en"), ("Tiếng Trung", "zh-CN"), ("Tiếng Nhật", "ja"), ("Tiếng Hàn", "ko")],
    format_func=lambda x: x[0]
)[1]

text_input = st.text_area("Nhập văn bản/kịch bản cần lồng tiếng cho video:", "Xin chào, đây là video thử nghiệm lồng tiếng tự động.")

if st.button("🚀 Bắt đầu lồng tiếng"):
    if uploaded_file is not None and text_input.strip() != "":
        with st.spinner("Đang xử lý video và tạo giọng đọc..."):
            try:
                # Lưu video tải lên
                with open("input_video.mp4", "wb") as f:
                    f.write(uploaded_file.read())

                # Dịch văn bản dùng deep-translator
                translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text_input)
                st.info(f"Văn bản đã dịch: {translated_text}")

                # Tạo âm thanh lồng tiếng từ gTTS
                tts = gTTS(text=translated_text, lang=target_lang.lower())
                tts.save("voice.mp3")

                # Ghép âm thanh vào video
                video = VideoFileClip("input_video.mp4")
                audio = AudioFileClip("voice.mp3")

                final_video = video.set_audio(audio)
                output_path = "output_video.mp4"
                final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

                st.success("🎉 Xử lý hoàn tất!")
                st.video(output_path)

                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Tải Video Hoàn Chỉnh Về Máy",
                        data=file,
                        file_name="video_long_tieng.mp4",
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"Có lỗi xảy ra trong quá trình xử lý: {e}")
    else:
        st.warning("Vui lòng tải lên video và nhập nội dung kịch bản!")
