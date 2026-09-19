# FROM python:3.12-slim
# WORKDIR /home/appuser/app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# RUN groupadd --gid 10001 appgroup && \
#     useradd --uid 10001 --gid appgroup --shell /bin/bash --create-home appuser
# COPY --chown=appuser:appgroup . .
# COPY ./app/main.py .
# EXPOSE 8000
# USER appuser
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir \
    -r requirements.txt
COPY main.py .
EXPOSE 8000
CMD [ "uvicorn", "main:app","--host","0.0.0.0","--port","8000"]