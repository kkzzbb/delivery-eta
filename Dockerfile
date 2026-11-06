FROM python:3.12-slim
 
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
 
WORKDIR /app
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY src/ ./src/
COPY model.bin ./
 
ENV PORT=9696
EXPOSE 9696

CMD ["sh", "-c", "uvicorn src.predict:app --host 0.0.0.0 --port ${PORT}"]
 