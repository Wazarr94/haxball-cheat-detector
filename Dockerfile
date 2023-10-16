# Use the official Python image as the base image
FROM python:3.10

# Install pnpm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g pnpm

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pnpm install

# Run the command
CMD ["pnpm", "run", "dev"]
