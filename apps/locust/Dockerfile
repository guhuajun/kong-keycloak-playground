FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1

WORKDIR /app/

RUN pip install locust python-keycloak \
	--index-url http://mirrors.aliyun.com/pypi/simple/ \
	--trusted-host mirrors.aliyun.com

ADD app/ .

EXPOSE 5557 8089

CMD ["locust", "--host", "http://shop:8000"]