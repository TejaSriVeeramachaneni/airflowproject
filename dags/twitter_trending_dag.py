from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.empty import EmptyOperator
from tweepy.errors import TooManyRequests

from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from textblob import TextBlob
import tweepy
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_summary(**kwargs):
    file_path = '/opt/airflow/dags/output/twitter_trends_sentiment.json'
    with open(file_path, 'r') as f:
        tweets = json.load(f)

    total = len(tweets)
    pos = sum(1 for t in tweets if t['sentiment'] > 0)
    neg = sum(1 for t in tweets if t['sentiment'] < 0)
    neu = total - pos - neg

    # Email content
    subject = "📊 Daily Twitter Sentiment Report"
    body = f"""
    Hello Teja,<br><br>
    Here is your daily Twitter sentiment report:<br><br>
    ✅ Total Tweets: <b>{total}</b><br>
    😊 Positive: <b>{pos}</b><br>
    😐 Neutral: <b>{neu}</b><br>
    😡 Negative: <b>{neg}</b><br><br>
    File has been successfully uploaded to your S3 bucket.<br><br>
    Regards,<br>
    Your Airflow Bot
    """

    # Setup email
    sender_email = ""
    receiver_email = ""   # Replace with your actual email
    app_password = ""        # Your Gmail App Password

    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", str(e))


# ------------------- Twitter API credentials -------------------
BEARER_TOKEN = "" # replace with your bearer api token

# ------------------- Output Directory -------------------
OUTPUT_DIR = "/opt/airflow/dags/output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "twitter_trends_sentiment.json")

# ------------------- Task 1: Fetch Tweets & Analyze Sentiment -------------------

def fetch_and_analyze_tweets(**kwargs):
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    query = "trending -is:retweet lang:en"

    try:
        tweets = client.search_recent_tweets(query=query, max_results=10, tweet_fields=["created_at", "text"])
    except TooManyRequests:
        print("⚠ Rate limit hit! Skipping this run.")
        return

    if not tweets.data:
        print("⚠ No tweets returned. Skipping.")
        return

    results = []
    for tweet in tweets.data:
        text = tweet.text
        sentiment = TextBlob(text).sentiment.polarity
        results.append({
            "text": text,
            "created_at": tweet.created_at.isoformat(),
            "sentiment": sentiment
        })

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "twitter_trends_sentiment.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"✅ Saved {len(results)} tweets with sentiment analysis to {output_file}")


# ------------------- Task 2: Upload to S3 -------------------
def upload_to_s3(**kwargs):
    s3_hook = S3Hook(aws_conn_id='aws_default')
    s3_hook.load_file(
        filename=OUTPUT_FILE,
        key='twitter_trends_sentiment.json',
        bucket_name='',#replace with your aws bucket name 
        replace=True
    )
    print("✅ Uploaded to S3 successfully.")

# ------------------- DAG Default Args -------------------
default_args = {
    'owner': 'Teja',
    'retries': 1,
    'retry_delay': timedelta(minutes=15)
}

# ------------------- DAG Definition -------------------
with DAG(
    dag_id='twitter_trending_pipeline',
    description='Pipeline to fetch Twitter trending tweets and analyze sentiment',
    schedule_interval='@daily',
    start_date=datetime(2025, 4, 1),
    catchup=False,
    default_args=default_args,
    tags=['twitter', 'sentiment']
) as dag:

    # Start Task
    start_pipeline = EmptyOperator(task_id='start_pipeline')

    # Task: Fetch + Analyze
    fetch_trending_tweets = PythonOperator(
        task_id='fetch_trending_tweets',
        python_callable=fetch_and_analyze_tweets,
        provide_context=True
    )

    # Task: Upload to S3
    upload_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3,
        provide_context=True
    )

    #Task : email alerts 
    send_email = PythonOperator(
    task_id='send_email_summary',
    python_callable=send_email_summary,
    provide_context=True
)


    # Task Dependencies
    start_pipeline >> fetch_trending_tweets >> upload_task >> send_email

