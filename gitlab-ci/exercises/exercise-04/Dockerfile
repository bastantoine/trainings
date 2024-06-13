# Using lightweight alpine image
FROM python:3.11

# Defining working directory and adding source code
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY bootstrap.sh ./bootstrap.sh
COPY accounting ./accounting

# Start app
EXPOSE 5000
ENTRYPOINT ["/usr/src/app/bootstrap.sh"]
