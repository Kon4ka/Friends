FROM python:3.9

ADD . /app

WORKDIR /app

# Run the command inside your image filesystem
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN python create-superuser.py