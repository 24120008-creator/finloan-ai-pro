# 🏦 FinLoan AI PRO

Ứng dụng Streamlit mô phỏng khoản vay ngân hàng + trợ lý AI.

## Chức năng

- Trang bìa ngân hàng.
- Máy tính khoản vay.
- Vay mua nhà, xe, tiêu dùng, kinh doanh.
- Lịch trả nợ.
- Biểu đồ dư nợ, gốc/lãi.
- So sánh 3 phương án vay.
- Chatbot AI hỏi về khoản vay và các chủ đề ngoài lề.
- Xuất CSV.
- Sẵn sàng deploy GitHub + Streamlit Community Cloud.

## Cài đặt

```bash
pip install -r requirements.txt
streamlit run app.py
```

## API key

Tạo `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "YOUR_API_KEY"
OPENAI_MODEL = "gpt-5"
```

Không commit file này lên GitHub.

## Deploy

1. Tạo GitHub repository.
2. Upload toàn bộ project.
3. Mở Streamlit Community Cloud.
4. Chọn repository và `app.py`.
5. Vào Advanced settings → Secrets.
6. Thêm API key.
7. Deploy.

## Lưu ý

Đây là công cụ mô phỏng/giáo dục. Không dùng kết quả làm cam kết được duyệt vay.
