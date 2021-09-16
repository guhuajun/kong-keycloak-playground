FROM python:3.9-slim

WORKDIR /app/

RUN pip install starlette uvicorn \
    --index-url http://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

COPY main.py .

EXPOSE 8081

CMD [ "python", "main.py" ]