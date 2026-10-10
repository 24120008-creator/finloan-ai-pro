import os, base64
from datetime import datetime
import pandas as pd
import streamlit as st

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

st.set_page_config(
    page_title="FinLoan AI PRO",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Helpers ----------
def money(v):
    return f"{v:,.0f} đ".replace(",", ".")

def secret(name, default=""):
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)

def calc(principal, annual_rate, months):
    r = annual_rate / 100 / 12
    if r == 0:
        payment = principal / months
    else:
        payment = principal * r * (1+r)**months / ((1+r)**months - 1)

    balance = principal
    rows = []
    for m in range(1, months + 1):
        interest = balance * r
        principal_paid = payment - interest
        actual = payment
        if m == months:
            principal_paid = balance
            actual = principal_paid + interest
        end = max(0, balance - principal_paid)
        rows.append([m, balance, actual, principal_paid, interest, end])
        balance = end

    df = pd.DataFrame(rows, columns=[
        "Tháng", "Dư nợ đầu kỳ", "Thanh toán", "Gốc", "Lãi", "Dư nợ cuối kỳ"
    ])
    return payment, df

def ai_answer(question, context, history):
    if OpenAI is None:
        return "Chưa cài OpenAI SDK. Hãy chạy `pip install -r requirements.txt`."
    key = secret("OPENAI_API_KEY")
    if not key:
        return ("🔐 Chatbot chưa có API key. Vào **Streamlit → Settings → Secrets** "
                "và thêm `OPENAI_API_KEY`.")
    model = secret("OPENAI_MODEL", "gpt-5")
    client = OpenAI(api_key=key)

    recent = "\n".join(
        f"{'User' if x['role']=='user' else 'AI'}: {x['content']}"
        for x in history[-10:]
    )
    instructions = f"""
Bạn là FinLoan AI PRO, trợ lý thông minh bằng tiếng Việt.
Bạn có thể trả lời câu hỏi về khoản vay, ngân hàng, tài chính cá nhân,
tiết kiệm, lập ngân sách, công nghệ, học tập, công việc và các câu hỏi
đời sống thông thường. Không bắt buộc câu hỏi phải liên quan đến vay.

Quy tắc:
- Trả lời rõ ràng, thân thiện, có ví dụ khi cần.
- Không tự bịa chính sách/lãi suất hiện hành của ngân hàng.
- Với quyết định tài chính quan trọng, nêu rõ đây là thông tin tham khảo.
- Nếu có dữ liệu máy tính khoản vay, dùng dữ liệu đó để trả lời.
- Không nói người dùng chắc chắn được duyệt vay.

DỮ LIỆU KHOẢN VAY:
{context}

LỊCH SỬ:
{recent}
"""
    try:
        res = client.responses.create(
            model=model,
            instructions=instructions,
            input=question
        )
        return res.output_text
    except Exception as e:
        return f"⚠️ Không gọi được AI: `{type(e).__name__}`."

# ---------- Local cover ----------
cover = os.path.join(os.path.dirname(__file__), "assets", "bank_cover.svg")
try:
    data = base64.b64encode(open(cover, "rb").read()).decode()
    cover_url = f"data:image/svg+xml;base64,{data}"
except Exception:
    cover_url = "https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1800&q=85"

st.markdown(f"""
<style>
.stApp {{background:linear-gradient(135deg,#f5f9ff,#fff 50%,#eef6ff);}}
[data-testid="stSidebar"] {{background:#092442;}}
[data-testid="stSidebar"] * {{color:white !important;}}
.hero {{
 min-height:390px;border-radius:28px;padding:50px;
 color:white;display:flex;align-items:center;
 background:linear-gradient(90deg,rgba(4,23,48,.96),rgba(4,23,48,.5)),
 url("{cover_url}") center/cover;
 box-shadow:0 18px 45px rgba(10,45,80,.2);
}}
.hero h1 {{font-size:58px;margin:0;letter-spacing:-2px;}}
.hero p {{font-size:19px;max-width:680px;line-height:1.6;}}
.card {{background:white;border:1px solid #e2eaf4;border-radius:20px;padding:20px;
box-shadow:0 8px 28px rgba(20,50,90,.07);height:100%;}}
.big {{font-size:27px;font-weight:800;color:#0b2d52;}}
.muted {{color:#6d7d91;}}
.chat-float {{
 position:fixed;right:24px;bottom:24px;background:#0b63ce;color:white;
 padding:13px 20px;border-radius:999px;box-shadow:0 8px 25px #174f8870;
 font-weight:700;z-index:99;
}}
</style>
""", unsafe_allow_html=True)

# ---------- State ----------
if "result" not in st.session_state:
    st.session_state.result = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "compare" not in st.session_state:
    st.session_state.compare = None

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🏦 FinLoan AI PRO")
    st.caption("Smart Banking Assistant")
    st.divider()
    page = st.radio(
        "Menu",
        ["🏠 Tổng quan", "🧮 Máy tính PRO", "🏦 So sánh ngân hàng",
         "🤖 Chatbot AI", "📊 Báo cáo & biểu đồ", "📚 Hướng dẫn"],
        label_visibility="collapsed"
    )
    st.divider()
    st.markdown("### 🤖 AI")
    st.success("Đã có API key" if secret("OPENAI_API_KEY") else "Chưa có API key")
    if st.button("🗑️ Xóa hội thoại", use_container_width=True
