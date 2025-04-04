FROM apache/airflow:2.7.3-python3.10

# Switch to airflow user
USER airflow

# Install Python packages
RUN pip install --no-cache-dir tweepy textblob
