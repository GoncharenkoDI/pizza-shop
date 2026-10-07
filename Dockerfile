FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY bot ./bot

ENTRYPOINT [ "/entrypoint.sh" ]
