FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir "uv>=0.1.15"
RUN uv pip install --no-cache-dir -r requirements.txt
COPY . .
ENV GEMINI_API_KEY=""
ENV CONVERT_API_KEY=""
CMD ["python", "-u", "src/agent.py"]