FROM python:3.10

WORKDIR /src

RUN pip install pipenv
RUN apt-get update && apt-get install -y netcat

COPY . .

RUN pipenv install --system

CMD ["echo", "hello"]
RUN useradd appuser && chown -R appuser /src
USER appuser

RUN ["chmod", "+x", "/src/entrypoint.sh"]

ENTRYPOINT ["sh", "/src/entrypoint.sh"]