FROM python:3-slim
MAINTAINER KeyboardInterrupt

# Install Requirements
RUN apt-get update -y && apt-get install -y python3-dev default-libmysqlclient-dev python-pip
RUN mkdir -p /data/uploads/creatures /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

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
CMD ["run.py"]
