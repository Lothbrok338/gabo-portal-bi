FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
# Ephemeral build-only settings: never used for live sessions.
RUN DEBUG=0 DJANGO_SECRET_KEY=build-only-for-collectstatic ALLOWED_HOSTS=localhost python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["sh", "-c", "exec gunicorn portal.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 2 --timeout 60"]
