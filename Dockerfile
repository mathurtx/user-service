FROM ubuntu:16.10

RUN  apt-get update \
  && apt-get install -y wget \
  python3.6 \
  && rm -rf /var/lib/apt/lists/*

RUN wget https://bootstrap.pypa.io/get-pip.py 
RUN python3.6 get-pip.py

RUN apt-get update && apt-get install -y curl

# Add files.
ADD bin/rabbitmq-start /usr/local/bin/

# Install RabbitMQ.
RUN \
  wget -qO - https://www.rabbitmq.com/rabbitmq-signing-key-public.asc | apt-key add - && \
  echo "deb http://www.rabbitmq.com/debian/ testing main" > /etc/apt/sources.list.d/rabbitmq.list && \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated rabbitmq-server && \
  rm -rf /var/lib/apt/lists/* && \
  rabbitmq-plugins enable rabbitmq_management && \
  echo "[{rabbit, [{loopback_users, []}]}]." > /etc/rabbitmq/rabbitmq.config && \
  chmod +x /usr/local/bin/rabbitmq-start


# Define environment variables.
ENV RABBITMQ_LOG_BASE /data/log
ENV RABBITMQ_MNESIA_BASE /data/mnesia

# Define mount points.
VOLUME ["/data/log", "/data/mnesia"]

# Define default command.

WORKDIR /user_service
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
COPY ./user_consumer_service/ ../user_consumer_service/
EXPOSE 8000
EXPOSE 5672
EXPOSE 15672
#RUN chmod +x bin/run_test.sh && bin/run_test.sh
CMD ["rabbitmq-start"]
CMD ["python3.6", "manage.py", "runserver", "127.0.0.1:8000"]