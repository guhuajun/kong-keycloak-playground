FROM python:3.9-slim

WORKDIR /app/

RUN pip install starlette uvicorn Authlib httpx \
    --index-url http://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

COPY ./src/ .

EXPOSE 8081

CMD [ "python", "main.py" ]