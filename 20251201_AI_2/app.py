from flask import Flask, render_template, request
import csv
from collections import defaultdict

app = Flask(__name__)

# CSV読み込み
def load_movies():
    movies = {}
    with open("movies_100k.csv", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for row in reader:
            if len(row) < 2:
                continue
            movies[row[0]] = row[1]
    return movies

def load_ratings():
    ratings = []
    with open("ratings_100k.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            ratings.append({
                "user": row[0],
                "movie": row[1],
                "rating": float(row[2])
            })
    return ratings

movies = load_movies()
ratings = load_ratings()

# 平均評価計算
def average_ratings():
    score = defaultdict(list)
    for r in ratings:
        score[r["movie"]].append(r["rating"])

    avg = {}
    for m, s in score.items():
        avg[m] = sum(s) / len(s)
    return avg

# レコメンド処理
def recommend_movies(selected):
    avg = average_ratings()
    scores = defaultdict(float)

    # 未選択の場合
    if len(selected) == 0:
        for movie, score in avg.items():
            scores[movie] = score
    else:
        for r in ratings:
            if r["movie"] in selected:
                for other in ratings:
                    if other["user"] == r["user"] and other["movie"] not in selected:
                        scores[other["movie"]] += other["rating"]

    top5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    return [(movies[movie], score) for movie, score in top5]

@app.route("/")
def index():
    return render_template("index.html", movies=movies)

@app.route("/recommend", methods=["POST"])
def recommend():
    selected = [
        request.form.get("movie1"),
        request.form.get("movie2"),
        request.form.get("movie3")
    ]
    selected = [m for m in selected if m]

    result = recommend_movies(selected)
    return render_template("recommend.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
