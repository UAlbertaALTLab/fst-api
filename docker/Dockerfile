FROM python:3.12-slim

WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pipenv install --deploy --system

# Copy application code
COPY . .

EXPOSE 8000

RUN python manage.py collectstatic --noinput

# Run the application
CMD ["python", "-m", "gunicorn", "fst_api.wsgi:application", "--workers", "4", "--bind", "0.0.0.0:8000"]