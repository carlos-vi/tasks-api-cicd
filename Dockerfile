# Base image: minimal Debian with Python 3.11 already installed ("slim" = lightweight variant)
FROM python:3.11-slim

# Working directory inside the container; the following commands run here
WORKDIR /code

# The base image ships an old setuptools that bundles copies of other libraries
# (jaraco.context, wheel) with known vulnerabilities. Upgrading it fixes them
RUN pip install --no-cache-dir --upgrade setuptools wheel

# Dependencies first: as long as requirements.txt does not change,
# Docker reuses this cached layer and does not reinstall anything when the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then the code (what changes the most goes last to take advantage of the cache)
COPY app ./app

# Documents the port the app listens on (it does not publish it by itself)
EXPOSE 8000

# Command that runs when the container starts.
# --host 0.0.0.0 is required: with the default (127.0.0.1) the app
# would only be reachable from inside the container itself
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
