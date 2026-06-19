FROM python:3.12-slim
WORKDIR /app
COPY app/server.py .
RUN useradd -u 10001 appuser 
USER appuser
EXPOSE 8080
CMD ["python","server.py"]
