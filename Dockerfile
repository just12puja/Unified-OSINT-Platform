FROM python:3.11-slim

# -------------------------------
# System dependencies
# -------------------------------
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Environment variables
# -------------------------------
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -------------------------------
# Set working directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Install Python dependencies
# -------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Copy project files
# -------------------------------
COPY . .

# -------------------------------
# Expose Streamlit port
# -------------------------------
EXPOSE 8501

# -------------------------------
# Run Streamlit
# -------------------------------
CMD ["streamlit", "run", "unified_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
