# Start from a base image containing Python 3.11 (minimal OS version)
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /code

# Copy the requirements.txt file to working directory
COPY ./requirements.txt /code/requirements.txt

# Install the required Python packages
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the entire "server" directory into the container
COPY ./server /code/server

# Set the PYTHONPATH environment variable to allow imports from the "server" directory
ENV PYTHONPATH="$PYTHONPATH:/code/server"

# Expose port 8080 for external access
EXPOSE 8080

# Use uvicorn to start FastAPI from "server/py/main.py"
CMD ["uvicorn", "server.py.main:app", "--host", "0.0.0.0", "--port", "8080"]
