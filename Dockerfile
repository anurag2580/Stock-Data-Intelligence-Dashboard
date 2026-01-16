# python 
FROM python:3.10-slim
# set working directory
WORKDIR /app
# copy requirements file
COPY requirements.txt .
# install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# copy application code
COPY . .
# expose port
EXPOSE 8000
# run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]