FROM python:3.12.4

ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app"

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

COPY ./utilities ./utilities
COPY ./app.py ./streamlit_app.py

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]