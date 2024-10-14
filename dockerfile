
FROM python:3.12.3


# Labels as key value pair
LABEL Maintainer="maxxonair"

# Define inventory working directory
WORKDIR /usr/app/inventory

# Copy the entire repository into the working directory
COPY ./* ./

# Start the material library
CMD [ "python", "./app.py"]