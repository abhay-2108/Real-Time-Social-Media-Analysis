

# Real-Time Social Media(You Tube) Analysis Dashboard

A full-stack web application to **analyze, visualize, and monitor YouTube video performance** in real time. Built using **Flask**, **MongoDB**, and **Chart.js**, this dashboard fetches video data from your database and presents insights like views, likes, sentiment, engagement, and more in a clean, interactive UI — helping you track content performance with ease.

---

## 🔍 Key Features

- 🔗 Input any YouTube video URL to view its statistics.
- 📦 Real-time data fetched from MongoDB.
- 📊 Graphical visualization with Chart.js (views, likes, comments, watch time).
- 💬 Sentiment analysis of video comments.
- 📈 Calculates and displays engagement rate.
- 🧭 Displays when video was published — date, time, and weekday.
- 🧠 Responsive UI styled like YouTube Studio (light theme).

---

## 🖼️ Demo Preview
![image](https://github.com/user-attachments/assets/c6e19e68-f208-44d0-98df-7745cdc35853)

![image](https://github.com/user-attachments/assets/758fea4e-a963-485b-be38-a4ed06c6b35b)

![image](https://github.com/user-attachments/assets/bb303559-bcef-45ce-877d-d7cb0af25c54)

---

## 🚀 Tech Stack

| Component     | Technology       |
|---------------|------------------|
| Frontend      | HTML, CSS, JavaScript, Chart.js |
| Backend       | Python Flask     |
| Database      | MongoDB          |
| Visualization | Chart.js         |
| Templates     | Jinja2           |

---

## ⚙️ Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/abhay-2108/Real-Time-Social-Media-Analysis.git
cd Real-Time-Social-Media-Analysis
````

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB

Make sure MongoDB is running locally or use a cloud service. Update the MongoDB URI in `app.py`:

```python
client = MongoClient("mongodb://localhost:27017/")
```

### 5. Run the Application

```bash
python app.py
```

Visit: [http://localhost:5000](http://localhost:5000)

---

---

## 📈 Metrics Visualized

* 👁️ Views
* ❤️ Likes
* 💬 Comments
* ⏱️ Duration & Watch Time
* 😊 Sentiment Score
* 🔥 Trending Status
* 📌 Engagement Rate
* 📅 Published Day, Time, Month
* ⏳ Last Data Fetched


## 📄 License

This project is licensed under the [MIT License](LICENSE).

---
