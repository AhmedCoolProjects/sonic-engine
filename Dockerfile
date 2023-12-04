FROM python:3.9.18

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN pip install -r requirements.txt

RUN pip install /usr/src/app/

RUN git clone https://github.com/AhmedCoolProjects/sonic_engine_templates.git templates

WORKDIR /usr/src/app/templates/hello_world/

CMD ["python", "app.py"]