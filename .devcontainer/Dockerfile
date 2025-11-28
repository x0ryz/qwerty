# Використовуємо той самий образ, що і раніше, він чудовий
FROM mcr.microsoft.com/devcontainers/python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Встановлюємо системні залежності для Python-пакетів (Pillow, WeasyPrint і т.д.)
# Ми прибрали postgresql-client звідси, бо він буде у features
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Робоча директорія
WORKDIR /app

# Ми НЕ копіюємо requirements.txt і НЕ робимо pip install тут жорстко,
# тому що в Dev Container краще це робити через postCreateCommand,
# щоб не перезбирати образ при кожній зміні однієї бібліотеки.
# Але якщо хочете швидкого старту, можна залишити COPY, але це збільшує розмір шару.