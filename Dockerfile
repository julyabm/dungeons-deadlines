FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_PASSWORD=admin
ENV DJANGO_SUPERUSER_EMAIL=admin@exemplo.com

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD bash -c 'until echo > /dev/tcp/db/5432; do echo "Aguardando porta do banco..."; sleep 2; done' && \
  python manage.py migrate --noinput && \
  python manage.py seed_items && \
  python manage.py createsuperuser --noinput --full_name="Administrador RPG" || echo "Superusuário já existe ou pulado." && \
  python manage.py runserver 0.0.0.0:8000 --insecure
