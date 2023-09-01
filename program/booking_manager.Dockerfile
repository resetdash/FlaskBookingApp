FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt amqp.reqs.txt ./
RUN pip install --no-cache-dir -r http.reqs.txt -r amqp.reqs.txt
COPY ./booking_manager.py ./invokes.py ./amqp_setup.py ./
CMD [ "python", "./booking_manager.py" ]