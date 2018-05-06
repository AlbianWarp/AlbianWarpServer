FROM python:3-slim
MAINTAINER KeyboardInterrupt
RUN apt-get update -y
RUN apt-get install -y python3-dev libmysqlclient-dev python-pip
COPY . /app
WORKDIR /app
RUN mkdir -p /data/uploads/creatures
RUN pip install -r requirements.txt

# Environment variables
ENV AW_HOST 0.0.0.0
ENV AW_PORT 5000
ENV AW_SQLALCHEMY_DATABASE_URI "sqlite:////data/albianwarp_database.sqlite"
ENV AW_UPLOAD_FOLDER "/data/uploads/"
VOLUME "/data/"
ENTRYPOINT ["python"]
CMD ["run.py"]