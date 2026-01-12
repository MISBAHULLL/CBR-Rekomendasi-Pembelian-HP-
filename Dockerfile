FROM python:3.10-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy data file
COPY data.xlsx .

# Set environment
ENV PYTHONPATH=/app/backend

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]