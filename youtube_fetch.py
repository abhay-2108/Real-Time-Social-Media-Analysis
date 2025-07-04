import requests, json
from dotenv import load_dotenv
import os
import isodate
from datetime import datetime

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
import string
import nltk
from pymongo import MongoClient
import re
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('vader_lexicon')

load_dotenv()
API_KEY = os.environ.get("YOUTUBE_API_KEY")
MAX_RESULTS = 1
MAX_COMMENTS = 10

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))
sia = SentimentIntensityAnalyzer()

def extract_video_id(youtube_url):
    """
    Extracts the video ID from a YouTube URL.
    """
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, youtube_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

# def search_videos(query, max_results):
#     url = "https://www.googleapis.com/youtube/v3/search"
#     params = {
#         "part": "snippet",
#         "q": query,
#         "type": "video",
#         "maxResults": max_results,
#         "key": API_KEY
#     }

#     response = requests.get(url, params=params)
#     data = response.json()
#     return [item["id"]["videoId"] for item in data.get("items", [])]

def get_video_details(video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(video_ids),
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    video_data = []
    for item in data["items"]:
        details = {
            # Video Information
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "published_at": item["snippet"]["publishedAt"],
            "channel_title": item["snippet"]["channelTitle"],
            "tags": item["snippet"].get("tags", []),
            "category_id": item["snippet"]["categoryId"],
            "duration": item["contentDetails"]["duration"],
            "video_url": f"https://www.youtube.com/watch?v={item['id']}",

            # Engagement Metrics
            "view_count": item["statistics"].get("viewCount", 0),
            "like_count": item["statistics"].get("likeCount", 0),
            "comment_count": item["statistics"].get("commentCount", 0),
        }
        video_data.append(details)

    return video_data

def preprocess_comment(text):
    # Lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Tokenize
    tokens = word_tokenize(text)

    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]

    return " ".join(tokens)

def get_top_comments(video_id, max_comments=10):
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": max_comments,
        "textFormat": "plainText",
        "order": "time",  
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []

    data = response.json()
    comments = []

    for item in data.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comment_text = snippet["textDisplay"]
        author = snippet["authorDisplayName"]
        like_count = snippet["likeCount"]
        published_at = snippet["publishedAt"]

        # Preprocess comment
        clean_text = preprocess_comment(comment_text)

        # Sentiment score
        sentiment = sia.polarity_scores(clean_text)
        sentiment_label = (
            "positive" if sentiment["compound"] >= 0.05 else
            "negative" if sentiment["compound"] <= -0.05 else
            "neutral"
        )

        comments.append({
            "author": author,
            "original_comment": comment_text,
            "clean_comment": clean_text,
            "likes": like_count,
            "published_at": published_at,
            "sentiment": sentiment_label,
            "sentiment_score": sentiment["compound"]
        })

    return comments

def is_trending(video):
    from datetime import datetime

    view_count = int(video["view_count"])
    published_time = datetime.strptime(video["published_at"], "%Y-%m-%dT%H:%M:%SZ")
    hours_since_posted = (datetime.utcnow() - published_time).total_seconds() / 3600

    views_per_hour = view_count / hours_since_posted
    return views_per_hour > 300  # set threshold empirically

def convert_duration_to_minutes(iso_duration):
    duration = isodate.parse_duration(iso_duration)
    return round(duration.total_seconds() / 60, 2)

def get_day_hour_bucket(published_at):
    dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
    date_str = dt.strftime("%d-%m-%Y")
    month_str = dt.strftime("%B")
    year_str = dt.strftime("%Y")
    day_str = dt.strftime("%A")
    time_str = dt.strftime("%H:%M:%S")
    return {
        "date": date_str,
        "month": month_str,
        "year": year_str,
        "day": day_str,
        "time": time_str
    }

def calc_engagement_rate(video):
    likes = int(video.get("like_count", 0))
    comments = int(video.get("comment_count", 0))
    views = int(video.get("view_count", 1))  # Avoid division by 0
    enganement_rate = round((likes + comments) / views, 4) * 100

    engagement = (
        "Highly Engaging" if enganement_rate > 5 else
        "Moderately Engaging" if enganement_rate > 2 and enganement_rate <= 5 else
        "Slightly Engaging" if enganement_rate > 0 and enganement_rate <= 2 else
        "Low Engagement"
    )
    return engagement 

def fetch_and_update_youtube_data(video_url, mongo_uri="mongodb://localhost:27017/", collection_name="videos"):
    video_id = extract_video_id(video_url)
    video_details = get_video_details([video_id])
    if not video_details:
        print("No video details found.")
        return

    comment_details = get_top_comments(video_id, MAX_COMMENTS)
    sentiment = comment_details[0]["sentiment"]

    trending_status = is_trending(video_details[0])
    duration_minutes = convert_duration_to_minutes(video_details[0]["duration"])
    published_day_hour = get_day_hour_bucket(video_details[0]["published_at"])
    engagement = calc_engagement_rate(video_details[0])

    update_fields = {
        **video_details[0],
        "sentiment": sentiment,
        "trending_status": trending_status,
        "duration_minutes": duration_minutes,
        "published_day_hour": published_day_hour,
        "engagement_rate": engagement,
        "fetched_at": datetime.utcnow()
    }

    client = MongoClient(mongo_uri)
    db = client["youtube_db"]  # Always use the same database
    collection = db[collection_name]  # Use the collection_name parameter (video_id)
    collection.update_one(
        {"video_id": video_id},
        {"$set": update_fields},
        upsert=True
    )
    client.close()
