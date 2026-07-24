# Use an official Python runtime as a parent image
FROM python:3.10-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Install system build dependencies needed to compile C extensions like tgcrypto
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy installed python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Make sure scripts installed by pip are usable
ENV PATH=/root/.local/bin:$PATH

# Copy the rest of the application code
COPY . .

# Ensure proxies.txt exists during container startup
RUN touch proxies.txt

# Command to run the bot
CMD ["python", "bot.py"]
