FROM python:3.6

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./ /

ENTRYPOINT [ "python3", "app.py" ]