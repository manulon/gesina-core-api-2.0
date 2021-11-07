FROM python:3.8

ADD . /app/
WORKDIR /app/
RUN pip install pipenv
RUN pipenv install --system

CMD ["echo", "hello"]