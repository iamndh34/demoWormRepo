# 🚨 BẢNG LIỆT KÊ LỖI MONG ĐỢI (EXPECTED FINDINGS)
# ----------------------------------------------------------------------
# | STT | Agent Mục Tiêu  | Loại Lỗi (Error Category)      | Mô Tả Chi Tiết                               |
# |-----|-----------------|-------------------------------|----------------------------------------------|
# | 1   | devops-ariel    | Security: Root User           | Container chạy với quyền root                |
# | 2   | devops-ariel    | Perf: Layer Optimization      | Tách nhiều lệnh RUN gây phình image          |
# | 3   | devops-ariel    | Security: Secret Leak         | Dùng ARG để truyền GITHUB_TOKEN              |
# | 4   | devops-ariel    | Best Practice: Latest Tag     | Dùng tag 'latest' gây không ổn định          |
# ----------------------------------------------------------------------

FROM python:latest

# Lỗi: Lộ secret trong docker history
ARG GITHUB_TOKEN=ghp_secret_123456789

# Lỗi: Chạy quyền root
USER root

# Lỗi: Không gộp lệnh RUN, tạo nhiều layer thừa
RUN apt-get update
RUN apt-get install -y gcc

COPY . /app
WORKDIR /app

RUN pip install fastapi uvicorn

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
