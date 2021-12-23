FROM python:3-slim
MAINTAINER KeyboardInterrupt

# Install Requirements
RUN apt-get update -y && apt-get install -y default-libmysqlclient-dev python3-pip python3-wheel
RUN mkdir -p /data/uploads/creatures /app
WORKDIR /app
COPY requirements.txt /app
RUN python3 -m pip install -r requirements.txt

# Environment variables
ENV AW_HOST 0.0.0.0
ENV AW_PORT 5000
ENV AW_SQLALCHEMY_DATABASE_URI "sqlite:////data/albianwarp_database.sqlite"
ENV AW_UPLOAD_FOLDER "/data/uploads/"

# Copy Application into Image/Container
COPY . /app

# Volumes, Ports & Entrypoint
VOLUME "/data/"
EXPOSE 5000:5000
ENTRYPOINT ["python"]
CMD [ "-u", "run.py"]
