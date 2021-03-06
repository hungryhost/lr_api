FROM python:3.8.6 as builder

WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.8.6

# installing netcat (nc) since we are using that to listen to postgres server in entrypoint.sh
RUN apt-get update && apt-get install -y --no-install-recommends netcat && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install dependencies
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# set work directory
WORKDIR /usr/src/app

ADD . /usr/src/app
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN mkdir  ./logs/
RUN chmod 755 -R /usr/src/app/
RUN chmod +x /usr/src/app/entrypoint.sh
RUN chmod +rwx ./logs/
# run entrypoint.sh

CMD  ['python manage.py migrate --noinput']