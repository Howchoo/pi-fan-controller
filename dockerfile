FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
CMD ["pip3 install -r requirements.txt"]
COPY . .
CMD ["fancontrol.py"]
ENTRYPOINT ["python3"]