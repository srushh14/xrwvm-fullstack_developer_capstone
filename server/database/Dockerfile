# Build the React frontend
FROM node:18-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package*.json ./

RUN npm install

COPY frontend/ ./

RUN npm run build


# Build the Django application
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy the compiled React application
COPY --from=frontend-build /frontend/build /app/frontend/build

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "djangoproj.wsgi:application", "--bind", "0.0.0.0:8000"]