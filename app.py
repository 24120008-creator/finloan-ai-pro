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
    if st.button("🗑️ Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------- Home ----------
if page == "🏠 Tổng quan":
    st.markdown(f"""
    <div class="hero">
      <div>
        <div>🏦 FINLOAN AI PRO • SMART FINANCE</div>
        <h1>Quản lý khoản vay<br>thông minh.</h1>
        <p>Máy tính khoản vay, biểu đồ, so sánh phương án và trợ lý AI trong một ứng dụng.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    a,b,c,d = st.columns(4)
    cards = [
        ("🧮","Tính khoản vay","Theo dư nợ giảm dần"),
        ("📊","Phân tích","Gốc • lãi • dư nợ"),
        ("🏦","So sánh","Nhiều phương án"),
        ("🤖","AI PRO","Hỏi nhiều chủ đề"),
    ]
    for col,(icon,title,desc) in zip([a,b,c,d],cards):
        with col:
            st.markdown(f'<div class="card"><div style="font-size:32px">{icon}</div><h3>{title}</h3><p class="muted">{desc}</p></div>',unsafe_allow_html=True)
    st.write("")
    st.info("💡 Bắt đầu tại **Máy tính PRO**, sau đó mở **Báo cáo & biểu đồ** hoặc hỏi **Chatbot AI**.")

# ---------- Calculator ----------
elif page == "🧮 Máy tính PRO":
    st.title("🧮 Máy tính khoản vay PRO")
    loan_type = st.selectbox("Mục đích vay", ["Vay mua nhà","Vay mua xe","Vay tiêu dùng","Vay kinh doanh","Khác"])
    c1,c2,c3 = st.columns(3)
    with c1:
        principal = st.number_input("Số tiền vay (VNĐ)", 1_000_000, 50_000_000_000, 500_000_000, 10_000_000)
    with c2:
        rate = st.number_input("Lãi suất (%/năm)", 0.0, 50.0, 10.5, 0.1)
    with c3:
        months = st.slider("Kỳ hạn (tháng)",1,360,60)

    if st.button("🚀 Tính khoản vay", type="primary", use_container_width=True):
        pay, df = calc(principal,rate,months)
        st.session_state.result = {
            "type":loan_type,"principal":principal,"rate":rate,"months":months,
            "payment":pay,"df":df
        }

    r = st.session_state.result
    if r:
        total = r["df"]["Thanh toán"].sum()
        interest = r["df"]["Lãi"].sum()
        x,y,z = st.columns(3)
        for col,label,val in [(x,"Trả hàng tháng",r["payment"]),(y,"Tổng tiền trả",total),(z,"Tổng tiền lãi",interest)]:
            with col:
                st.markdown(f'<div class="card"><div class="muted">{label}</div><div class="big">{money(val)}</div></div>',unsafe_allow_html=True)
        st.write("")
        st.markdown("### 📅 Lịch trả nợ")
        show = r["df"].copy()
        for col in show.columns[1:]:
            show[col] = show[col].map(money)
        st.dataframe(show,use_container_width=True,hide_index=True,height=420)
        st.download_button("⬇️ Tải CSV",r["df"].to_csv(index=False).encode("utf-8-sig"),
                           "lich_tra_no.csv","text/csv")
        st.session_state.loan_context = (
            f"Mục đích: {r['type']}; vay {money(r['principal'])}; "
            f"lãi {r['rate']}%/năm; kỳ hạn {r['months']} tháng; "
            f"trả tháng {money(r['payment'])}; tổng lãi {money(interest)}."
        )

# ---------- Comparison ----------
elif page == "🏦 So sánh ngân hàng":
    st.title("🏦 So sánh phương án vay")
    st.caption("Nhập lãi suất bạn đang được báo/đang muốn mô phỏng. Đây không phải bảng lãi suất chính thức.")
    principal = st.number_input("Số tiền vay",1_000_000,50_000_000_000,500_000_000,10_000_000,key="cp")
    months = st.slider("Kỳ hạn",1,360,60,key="cm")
    cols = st.columns(3)
    banks = []
    defaults = [("Ngân hàng A",9.5),("Ngân hàng B",10.2),("Ngân hàng C",11.0)]
    for i,(name,default) in enumerate(defaults):
        with cols[i]:
            n=st.text_input("Tên phương án",name,key=f"bn{i}")
            rr=st.number_input("Lãi suất %/năm",0.0,50.0,default,0.1,key=f"br{i}")
            p,df=calc(principal,rr,months)
            banks.append({"Phương án":n,"Lãi suất":rr,"Trả/tháng":p,
                          "Tổng trả":df["Thanh toán"].sum(),"Tổng lãi":df["Lãi"].sum()})
    comp=pd.DataFrame(banks).sort_values("Tổng lãi")
    st.markdown("### 🏆 Kết quả")
    display=comp.copy()
    for c in ["Trả/tháng","Tổng trả","Tổng lãi"]:
        display[c]=display[c].map(money)
    st.dataframe(display,use_container_width=True,hide_index=True)
    best=comp.iloc[0]
    st.success(f"Phương án có tổng lãi thấp nhất trong dữ liệu bạn nhập: **{best['Phương án']}** — {money(best['Tổng lãi'])}.")

# ---------- Chatbot ----------
elif page == "🤖 Chatbot AI":
    st.title("🤖 FinLoan AI PRO")
    st.markdown("Bạn có thể hỏi **khoản vay hoặc bất kỳ câu hỏi phù hợp nào**.")
    if st.session_state.get("loan_context"):
        with st.expander("📌 Ngữ cảnh khoản vay"):
            st.write(st.session_state.loan_context)

    examples = ["Vay 500 triệu 5 năm thì trả bao nhiêu?",
                "Làm sao để giảm tổng tiền lãi?",
                "Excel dùng để làm gì?",
                "Hãy giúp tôi viết CV xin việc"]
    qcols=st.columns(4)
    for i,e in enumerate(examples):
        with qcols[i]:
            if st.button(e,key=f"ex{i}",use_container_width=True):
                st.session_state.pending=e

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt=st.chat_input("Nhập câu hỏi...")
    if getattr(st.session_state,"pending",None):
        prompt=st.session_state.pending
        st.session_state.pending=None

    if prompt:
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("AI đang trả lời..."):
                ans=ai_answer(prompt,st.session_state.get("loan_context","Chưa có"),st.session_state.messages)
            st.markdown(ans)
        st.session_state.messages.append({"role":"assistant","content":ans})

# ---------- Charts ----------
elif page == "📊 Báo cáo & biểu đồ":
    st.title("📊 Báo cáo & biểu đồ")
    r=st.session_state.result
    if not r:
        st.warning("Hãy tính một khoản vay trước.")
    else:
        df=r["df"]
        st.subheader("Dư nợ theo thời gian")
        st.line_chart(df.set_index("Tháng")[["Dư nợ cuối kỳ"]])
        st.subheader("Gốc và lãi từng tháng")
        st.bar_chart(df.set_index("Tháng")[["Gốc","Lãi"]])
        total=df["Thanh toán"].sum()
        interest=df["Lãi"].sum()
        st.markdown(f"""
        <div class="card">
        <h3>📄 Tóm tắt báo cáo</h3>
        <p>Khoản vay: <b>{money(r['principal'])}</b></p>
        <p>Lãi suất: <b>{r['rate']}%/năm</b></p>
        <p>Kỳ hạn: <b>{r['months']} tháng</b></p>
        <p>Khoản trả tháng: <b>{money(r['payment'])}</b></p>
        <p>Tổng lãi dự kiến: <b>{money(interest)}</b></p>
        <p>Tổng thanh toán: <b>{money(total)}</b></p>
        </div>
        """,unsafe_allow_html=True)

# ---------- Guide ----------
else:
    st.title("📚 Hướng dẫn")
    st.markdown("""
### 1. Chạy trên máy
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 2. Bật AI
Tạo `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "YOUR_API_KEY"
OPENAI_MODEL = "gpt-5"
```

### 3. Deploy GitHub
Upload toàn bộ project lên GitHub → Streamlit Community Cloud → chọn repository → `app.py`.

### 4. Secret trên Streamlit Cloud
Vào **Advanced settings → Secrets** và dán:
```toml
OPENAI_API_KEY = "YOUR_API_KEY"
OPENAI_MODEL = "gpt-5"
```

### 5. Lưu ý
Kết quả là mô phỏng. Lãi suất, phí, bảo hiểm và cách tính thực tế của ngân hàng có thể khác.
""")

st.markdown('<div class="chat-float">🤖 FinLoan AI</div>',unsafe_allow_html=True)
st.caption(f"FinLoan AI PRO • {datetime.now().year} • Công cụ tham khảo")
