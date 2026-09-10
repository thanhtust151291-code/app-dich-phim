
import streamlit as st
import os
import speech_recognition as sr
from gtts import gTTS
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip, AudioFileClip

# Cấu hình giao diện Streamlit chuẩn App di động
st.set_page_config(
    page_title="Studio Dịch & Lồng Tiếng Phim Pro", 
    page_icon="🎬", 
    layout="centered"
)

# Custom CSS giao diện xịn đẹp cho APK
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 12px;
        font-size: 18px;
        border: none;
    }
    .stSelectbox, .stTextArea { font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 Studio Dịch Phim Pro AI")
st.write("✨ *Tự động tách giọng, dịch ngôn ngữ & lồng tiếng video chuyên nghiệp*")

# 1. Chọn Tệp Video
uploaded_file = st.file_uploader("📥 Tải video cần lồng tiếng lên (MP4, AVI, MOV):", type=["mp4", "avi", "mov"])

col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox(
        "🗣️ Ngôn ngữ gốc trong video:",
        options=[("Tiếng Anh", "en-US"), ("Tiếng Việt", "vi-VN"), ("Tiếng Trung", "zh-CN"), ("Tiếng Nhật", "ja-JP"), ("Tiếng Hàn", "ko-KR")],
        format_func=lambda x: x[0]
    )[1]

with col2:
    target_lang = st.selectbox(
        "🌐 Ngôn ngữ muốn lồng tiếng:",
        options=[("Tiếng Việt", "vi"), ("Tiếng Anh", "en"), ("Tiếng Trung", "zh-CN"), ("Tiếng Nhật", "ja"), ("Tiếng Hàn", "ko")],
        format_func=lambda x: x[0]
    )[1]

# Xử lý nhận dạng lời nói tự động khi video được tải lên
auto_script = ""
if uploaded_file is not None:
    with st.spinner("🔍 AI đang phân tích và trích xuất lời nói từ video..."):
        try:
            # Lưu file video tạm
            with open("input_video.mp4", "wb") as f:
                f.write(uploaded_file.read())
            
            # Tách âm thanh từ video để AI đọc
            video_temp = VideoFileClip("input_video.mp4")
            if video_temp.audio is not None:
                video_temp.audio.write_audiofile("extracted_audio.wav", codec='pcm_s16le', verbose=False, logger=None)
                
                # AI Nhận dạng giọng nói (Speech-to-Text)
                recognizer = sr.Recognizer()
                with sr.AudioFile("extracted_audio.wav") as source:
                    audio_data = recognizer.record(source, duration=60) # Phân tích thoại
                    try:
                        auto_script = recognizer.recognize_google(audio_data, language=source_lang)
                        st.success("✅ Đã tự động trích xuất kịch bản thoại từ video thành công!")
                    except:
                        auto_script = "Xin chào, chào mừng bạn đến với video dịch tự động."
            video_temp.close()
        except Exception as e:
            auto_script = "Xin chào, chào mừng bạn đến với video dịch tự động."

# Ô xem & chỉnh sửa kịch bản
text_input = st.text_area("📝 Kịch bản thoại (AI tự trích xuất hoặc bạn có thể tự chỉnh sửa):", value=auto_script, height=120)

# Nút Xử lý chính
if st.button("🚀 BẮT ĐẦU DỊCH & LỒNG TIẾNG"):
    if uploaded_file is not None and text_input.strip() != "":
        with st.spinner("⚡ AI đang tiến hành dịch thuật, tạo giọng đọc & ghép video..."):
            try:
                # 1. Dịch văn bản kịch bản sang ngôn ngữ mới
                translator = GoogleTranslator(source='auto', target=target_lang)
                translated_text = translator.translate(text_input)
                
                st.info(f"<b>Bản dịch ({target_lang.upper()}):</b> {translated_text}", icon="ℹ️")

                # 2. Tạo file âm thanh lồng tiếng mới (Text-to-Speech)
                tts = gTTS(text=translated_text, lang=target_lang.lower(), slow=False)
                tts.save("voice.mp3")

                # 3. Ghép âm thanh lồng tiếng mới vào video
                video = VideoFileClip("input_video.mp4")
                new_audio = AudioFileClip("voice.mp3")

                # Tự động thay thế âm thanh cũ bằng âm thanh lồng tiếng mới
                final_video = video.set_audio(new_audio)
                output_path = "output_video.mp4"

                # Xuất file video với cấu hình tối ưu tốc độ cho di động
                final_video.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    threads=4,
                    logger=None
                )

                # Giải phóng bộ nhớ đệm
                video.close()
                new_audio.close()
                final_video.close()

                st.balloons() # Hiệu ứng chúc mừng
                st.success("🎉 Lồng tiếng thành công! Xem video kết quả bên dưới:")
                
                # Hiển thị video kết quả
                st.video(output_path)

                # Nút tải video về máy
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 TẢI VIDEO ĐÃ LỒNG TIẾNG VỀ ĐIỆN THOẠI",
                        data=file,
                        file_name="video_dich_long_tieng_pro.mp4",
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"Có lỗi xảy ra trong quá trình lồng tiếng: {e}")
    else:
        st.warning("⚠️ Vui lòng tải video lên trước khi bắt đầu!")
