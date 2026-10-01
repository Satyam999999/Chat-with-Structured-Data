FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run the data generator during build, but ETL should be run at runtime or separately
RUN python generate_data.py

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/docs || exit 1

ENTRYPOINT ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
