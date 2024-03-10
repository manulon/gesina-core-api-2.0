FROM postman/newman as base
WORKDIR /etc/newman

RUN npm install -g newman-reporter-html
RUN npm install -g newman-reporter-json-summary

COPY ["test/", "./"]

ENTRYPOINT newman run gesina_api.postman_collection.json  --environment=testing.postman_environment.json --reporters cli
