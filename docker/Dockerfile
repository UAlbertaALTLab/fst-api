FROM python:3.12-slim

# Install pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pipenv install --deploy --system

# Copy application code
COPY . .

EXPOSE 8000

# Run the application
CMD ["python", "-m", "gunicorn", "fst_api.asgi:application", "-k", "uvicorn_worker.UvicornWorker", "--workers", "4"]