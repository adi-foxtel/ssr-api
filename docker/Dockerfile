FROM python:3.10-slim

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

RUN mkdir /ssr_api
WORKDIR /ssr_api
COPY . ./
RUN pip install .

EXPOSE 9001
ENTRYPOINT ["python", "-u", "/ssr_api/scripts/apifast.py"]
