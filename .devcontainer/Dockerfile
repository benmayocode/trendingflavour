# Base Python image
FROM python:3.10-slim

# Install OS-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Set workdir
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY . .

# Set environment variable
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port
EXPOSE 5000

# Start server in dev mode
CMD ["flask", "run"]
