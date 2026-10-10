import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Tải cấu hình từ file .env (nếu chạy local)
load_dotenv()

# Hàm lấy cấu hình bảo mật từ file .env hoặc Streamlit Secrets
def secret(key, default=None):
    if key in os.environ:
        return os.environ[key]
    elif hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    return default

# Hàm xử lý gửi câu hỏi lên OpenRouter
def ai_answer(question, instructions="You are a helpful assistant."):
    # 1. Lấy API Key từ cấu hình bảo mật
    key = secret("OPENAI_API_KEY")
    if not key:
        return ("🔐 Chatbot chưa có API key. Hãy thêm OPENAI_API_KEY vào file .env "
                "hoặc cấu hình trong Streamlit Settings -> Secrets.")
    
    # 2. Lấy tên model mong muốn (Mặc định dùng deepseek-r1 qua OpenRouter)
    model = secret("OPENAI_MODEL", "deepseek/deepseek-r1")
    
    try:
        # ĐÂY CHÍNH LÀ KHÚC ĐƯA API KEY VÀ BASE_URL CỦA OPENROUTER VÀO
        client = OpenAI(
            base_url="https://openrouter.ai",
            api_key=key
        )
        
        # Gọi API OpenRouter theo cấu trúc chuẩn chat.completions
        res = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": question}
            ]
        )
        # Trả về nội dung phản hồi của Bot
        return res.choices.message.content
        
    except Exception as e:
        return f"❌ Đã xảy ra lỗi khi kết nối với OpenRouter: {str(e)}"

# --- GIAO DIỆN STREAMLIT ---
st.set_page_config(page_title="OpenRouter AI Chatbot", page_icon="🤖")
st.title("🤖 OpenRouter AI Chatbot")
st.caption("Chatbot sử dụng mã nguồn Streamlit tích hợp OpenRouter API")

# Cấu hình lời nhắc hệ thống (Instructions) ở thanh bên cạnh
system_prompt = st.sidebar.text_area(
    "System Instructions (Vai trò của Bot)",
    value="Bạn là một trợ lý ảo tiếng Việt thông minh và thân thiện.",
    height=150
)

# Khởi tạo lịch sử chat trong session state của Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lại các tin nhắn cũ trong lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ô nhập câu hỏi của người dùng
if user_query := st.chat_input("Nhập câu hỏi của bạn vào đây..."):
    # Hiển thị tin nhắn người dùng vừa nhập
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Gọi AI trả lời và hiển thị hiệu ứng đang xử lý
    with st.chat_message("assistant"):
        with st.spinner("Đang suy nghĩ..."):
            bot_response = ai_answer(user_query, instructions=system_prompt)
            st.markdown(bot_response)
            
    # Lưu câu trả lời của bot vào lịch sử chat
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
