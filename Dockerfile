# Use Python 3.12.3
FROM python:3.12.3


# Labels as key value pair
LABEL Maintainer="maxxonair"

ENV TRAME_CLIENT_TYPE=vue2

# Install required packages 
RUN apt-get update -y 
RUN apt-get install zbar-tools libmariadb3 libmariadb-dev ffmpeg libsm6 libxext6 -y

# Define inventory working directory
WORKDIR /usr/app/inventory

# Make project file directories
RUN mkdir backend
RUN mkdir frontend
RUN mkdir frontend/data

# [COPY] all required files to run the application
COPY backend/* ./backend/
COPY frontend/* ./frontend/
COPY frontend/data/no_image_available.jpg ./frontend/data/no_image_available.jpg
COPY requirements.txt ./
COPY app.py ./
COPY __init__.py ./

# Install uv with pip (and use uv for dependency management from here 
# onwards)
RUN pip install uv 

# Create virtual environment with uv
RUN uv venv

# Install python dependencies
RUN uv pip install -r requirements.txt

# Start the UI server
CMD ["uv", "run", "app.py"]