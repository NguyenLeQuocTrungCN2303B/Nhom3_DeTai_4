FROM python:3.11-slim

WORKDIR /app

# Cập nhật và cài đặt các gói cần thiết cho WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    pkg-config \
    default-libmysqlclient-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libjpeg62-turbo-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt pip và các gói Python
COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

# Sao chép mã nguồn vào container
COPY . .

EXPOSE 8000

# Trong quá trình debug, entry point này sẽ bị ghi đè
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
