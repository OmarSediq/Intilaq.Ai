# المرحلة الأولى: إعداد البيئة وبناء الاعتماديات
FROM python:3.10-slim AS builder

# تثبيت الأدوات الأساسية
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# تثبيت dockerize
RUN wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
    && tar -xvzf dockerize-linux-amd64-v0.6.1.tar.gz -C /usr/local/bin \
    && rm dockerize-linux-amd64-v0.6.1.tar.gz

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملف الاعتماديات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# المرحلة الثانية: بناء الحاوية النهائية
FROM python:3.10-slim

# إعداد مجلد العمل
WORKDIR /app

# نسخ الاعتماديات المثبتة من مرحلة builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/include /usr/local/include

# نسخ الكود الخاص بالتطبيق
COPY . .

# تقليل صلاحيات المستخدم لأمان أكثر
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# فتح المنفذ
EXPOSE 8000

# بدء التطبيق مع انتظار PostgreSQL
CMD ["dockerize", "-wait", "tcp://postgres:5432", "-timeout", "60s", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
