FROM python:3
MAINTAINER yoloClin <yoloClin@github.com>

RUN pip install --no-cache-dir requests
RUN wget https://github.com/barnybug/cli53/releases/download/0.8.15/cli53-linux-amd64 -O /bin/cli53

COPY cli53.sha512sum /app/
COPY aws_dnydns.py /app/

RUN sha512sum -c /app/cli53.sha512sum && chmod +x /bin/cli53

WORKDIR /app/

CMD ["python3", "/app/aws_dnydns.py"]
