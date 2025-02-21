FROM python:3.10-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

FROM python:3.10-slim

WORKDIR /app

RUN echo "deb http://ftp.debian.org/debian bookworm contrib" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev \
       libcairo2 libpangoft2-1.0-0 libpangocairo-1.0-0 \
       libgdk-pixbuf2.0-0 libpangoxft-1.0-0 libfontconfig1 \
       libfreetype6 libjpeg62-turbo libffi-dev shared-mime-info \
       fonts-liberation fontconfig xfonts-utils cabextract \
       ttf-mscorefonts-installer \
       wkhtmltopdf \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

COPY . /app
COPY ./templates /app/app/templates

COPY alembic.ini /app/alembic.ini
COPY migrations /app/alembic

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
