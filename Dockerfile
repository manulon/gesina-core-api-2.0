FROM python:3.10

ADD src /app/
ADD Pipfile /app/
ADD Pipfile.lock /app/
ADD ina_resources/demo_ina /app/
ADD test /app/
WORKDIR /app/
RUN pip install pipenv
RUN pipenv install --system

CMD ["echo", "hello"]