# Use official lightweight Python image
FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Optional: install system dependencies (if needed)
# RUN apk add --no-cache gcc musl-dev

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the desired port
EXPOSE 3000

# Run the app
CMD ["python", "main.py"]
