FROM alpine:3.21

# Update and upgrade
RUN apk update && apk upgrade

# Install dependencies:
# - FFMPEG
# - Poetry
RUN apk add --update --no-cache "ffmpeg=~6.1" "poetry=~1.8"

# Copy project files
COPY . /app

# Set working directory
WORKDIR /app

# Install python dependencies
RUN poetry install --only main --no-root

# Run the application
CMD ["poetry", "run", "python3", "main.py"]
