FROM nikolaik/python-nodejs:python3.10-nodejs18-alpine

# Install pnpm
RUN npm install -g pnpm

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install rustup and cargo
RUN apk add rustup cargo && \
    rustup-init -y --no-modify-path --default-toolchain stable && \
    source $HOME/.cargo/env

# Install the dependencies
RUN pnpm install

# Run the command
CMD ["pnpm", "run", "dev"]
