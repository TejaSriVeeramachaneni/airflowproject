# 🐦 Twitter Trending Sentiment Analysis Pipeline

This project is an automated data pipeline built using **Apache Airflow**, designed to:

- Fetch real-time trending tweets from Twitter
- Perform sentiment analysis using **TextBlob**
- Store results in **AWS S3**
- Send a **daily email summary** with key sentiment insights

---

## 🚀 Project Highlights

- 🔁 **Automated Workflow**: Scheduled to run daily via Airflow
- 🐦 **Live Twitter Data**: Pulls recent tweets using Twitter API v2 via Tweepy
- 💬 **Sentiment Analysis**: Uses TextBlob to analyze tweet sentiment
- ☁️ **AWS S3 Storage**: Results pushed to an S3 bucket for persistence
- ✉️ **Email Alerts**: Gmail summary with sentiment breakdown

---

## 🧰 Tech Stack

| Tool           | Purpose                          |
|----------------|----------------------------------|
| Apache Airflow | DAG scheduling and orchestration |
| Python         | Core programming language        |
| Tweepy         | Twitter API access               |
| TextBlob       | Sentiment analysis               |
| AWS S3         | Cloud storage                    |
| SMTP (Gmail)   | Email summary notifications      |
| Docker         | Containerized Airflow setup      |

## ⚙️ How to Run This Project

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/TejaSriVeeramachaneni/airflow_twitter_project.git
cd airflow_twitter_project
2️⃣ Set Twitter API and Email Credentials
Update the following variables in twitter_trending_dag.py:

BEARER_TOKEN = ""               # Your Twitter API bearer token
sender_email = ""              # Your Gmail address
receiver_email = ""            # Recipient email
app_password = ""              # Gmail App Password
📌 You can also move these to a .env file for better security.

3️⃣ Start Airflow with Docker
docker-compose up airflow-init
# then start the services
docker-compose up -d
4️⃣ Access the Airflow UI
Navigate to: http://localhost:8080

Login credentials:
Username: airflow
Password: airflow
Trigger the DAG: twitter_trending_pipeline

📬 Sample Email Output
Subject: Daily Twitter Sentiment Report

✅ Total Tweets: 10  
😊 Positive: 6  
😐 Neutral: 3  
😡 Negative: 1  

File uploaded to: s3://your-bucket-name/twitter_trends_sentiment.json
🧠 Author Notes
This project was developed as a full pipeline demo with real-world integrations, built entirely from scratch using Docker + Airflow. Every part — from API integration to cloud upload and alerts — was designed hands-on for learning and production-ready workflows.

📄 License
This project is licensed under the Apache License 2.0.

🙋‍♂️ Let's Connect
Feel free to reach out if you'd like to collaborate or need help setting this up for your own use case!

💌 curiousteja15@gmail.com
