FROM python:3.6
WORKDIR /app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD ./drive2cloud ./
CMD ["python", "drive2cloud.py", "--reindex", "True", "--interval-hours", "24"]