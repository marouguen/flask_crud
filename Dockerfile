# Base Python image
FROM python:3.12.7-slim

# Set the working directory
WORKDIR /

# Copy all project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask app's port
EXPOSE 5000

# Default command to run the Flask app
CMD ["python", "app.py"]
