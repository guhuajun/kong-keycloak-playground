FROM python:3-slim

ADD sources.list /etc/apt/sources.list

RUN apt update && apt-get install -y iputils-ping net-tools tcpdump netcat

RUN pip install notebook scapy \
    --index-url http://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

WORKDIR /workspace/

CMD [ "jupyter", "notebook", "--ip", "0.0.0.0", "--allow-root" ]