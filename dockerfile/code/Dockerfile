FROM june666666/symp_env:symp_20221218

WORKDIR /code
COPY ./tmp/code/*.py /code/
COPY ./tmp/code/convid_pred /code/convid_pred
COPY ./tmp/code/symp_pred /code/symp_pred

RUN apt-get update && rm -rf /var/lib/apt/lists/*
EXPOSE 8088

CMD ["bash", "-c", "source activate sympl && python /code/manage.py runserver 0.0.0.0:8088"]

