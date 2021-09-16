FROM python:3.8-alpine

WORKDIR /app/

RUN pip install uvicorn starlette \
    --index-url http://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

COPY main.py .

EXPOSE 8000

CMD ["python", "main.py"]
