from flask import Flask, render_template, request
from youtube_fetch import fetch_and_update_youtube_data, extract_video_id
from pymongo import MongoClient
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

app = Flask(__name__)

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "youtube_db"
COLLECTION_NAME = "videos"

@app.route('/', methods=['GET', 'POST'])
def index():
    video_doc = None
    video_url = ""
    if request.method == 'POST':
        video_url = request.form['video_url']
        if video_url:
            video_id = extract_video_id(video_url)
            # Use video_id as the collection name
            fetch_and_update_youtube_data(
                video_url,
                mongo_uri=MONGO_URI,
                collection_name=video_id
            )
            client = MongoClient(MONGO_URI)
            db = client[DB_NAME]
            collection = db[video_id]  # Each video gets its own collection
            video_doc = collection.find_one({"video_id": video_id})
            client.close()
            return render_template('dashboard.html', video_doc=video_doc, video_url=video_url)
    return render_template('dashboard.html', video_doc=video_doc, video_url=video_url)

if __name__ == '__main__':
    app.run(debug=True)