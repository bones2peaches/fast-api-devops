FROM python:3.12.2-slim-bookworm AS base

# Perform necessary system updates and installs
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends git \
    && apt-get autoremove -y

FROM base AS install
WORKDIR /home/code

# Copy only the requirements.txt file to use for installations
COPY requirements.txt ./

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

FROM install as app-image

ENV PYTHONPATH=/home/code/ PYTHONHASHSEED=0

# Copy your application code
COPY tests/ tests/
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini config.ini pytest.ini ./

# Create a non-root user and switch to it for security
RUN addgroup --system --gid 1001 app-user \
    && adduser --system --uid 1001 app-user
USER app-user

ENV PYTHONDONTWRITEBYTECODE=1

# CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000" , "--reload"]
# CMD ["tail" , "-f" , "/dev/null"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000" , "--reload"]