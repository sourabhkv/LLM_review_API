# Use the official Python 3.12 image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install necessary packages for Selenium and Edge
RUN apt-get update && \
    apt-get install -y wget gnupg2 && \
    wget https://packages.microsoft.com/keys/microsoft.asc && \
    apt-key add microsoft.asc && \
    sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list' && \
    rm microsoft.asc && \
    apt-get update && \
    apt-get install -y microsoft-edge-stable

# Download and setup Edge WebDriver
RUN wget https://msedgedriver.azureedge.net/$(microsoft-edge --version | awk '{print $3}')/edgedriver_linux64.zip && \
    apt-get install -y unzip && \
    unzip edgedriver_linux64.zip && \
    rm edgedriver_linux64.zip && \
    mv msedgedriver /usr/local/bin/

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
