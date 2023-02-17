FROM tiangolo/uwsgi-nginx:python3.10
ENV STATIC_URL /static
ENV STATIC_PATH /app/static
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
