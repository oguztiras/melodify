FROM python:3.11-slim

# Environment variables | not to create .pyc file | python logs
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# Work directory setting
WORKDIR /app

# Dependencies installing
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Project file copying
COPY . .

# Executable command
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]