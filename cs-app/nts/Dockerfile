FROM python:3.11-slim

# Run python interpreter in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Set working dir
WORKDIR /nts

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements file to docker FS
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip
# Install required python packages
RUN pip install -r requirements.txt

# Copy app code to docker FS
COPY . .

# Indicate port to expose during run
EXPOSE 8000

# Get the app up using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]