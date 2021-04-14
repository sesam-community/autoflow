FROM python:3-alpine
RUN apk update
RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
WORKDIR /app
COPY . .
EXPOSE 5000 
CMD ["python3","-u","service.py"]