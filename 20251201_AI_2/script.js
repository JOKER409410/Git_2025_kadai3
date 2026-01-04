let movies = [];
let ratings = [];

// CSV読み込み
async function loadCSV(path) {
  const res = await fetch(path);
  const text = await res.text();
  return text.split("\n").slice(1).map(row => row.split(","));
}

// 初期化
async function init() {
  const movieRows = await loadCSV("movies_100k.csv");
  const ratingRows = await loadCSV("ratings_100k.csv");

  movies = movieRows.map(r => ({
    movieId: r[0],
    title: r[1]
  }));

  ratings = ratingRows.map(r => ({
    userId: r[0],
    movieId: r[1],
    rating: Number(r[2])
  }));

  renderMovieList();
}

function renderMovieList() {
  const container = document.getElementById("movie-list");
  movies.slice(0, 50).forEach(movie => {
    const label = document.createElement("label");
    label.innerHTML = `
      <input type="checkbox" value="${movie.movieId}">
      ${movie.title}
    `;
    container.appendChild(label);
    container.appendChild(document.createElement("br"));
  });
}

// 平均評価計算
function calcAverageRatings() {
  const map = {};
  ratings.forEach(r => {
    if (!map[r.movieId]) map[r.movieId] = [];
    map[r.movieId].push(r.rating);
  });

  const avg = {};
  Object.keys(map).forEach(id => {
    avg[id] =
      map[id].reduce((a, b) => a + b, 0) / map[id].length;
  });
  return avg;
}

// レコメンド処理
function recommend(selectedIds) {
  const avgRatings = calcAverageRatings();

  let scores = {};

  if (selectedIds.length === 0) {
    // 未選択 → 高評価映画
    scores = avgRatings;
  } else {
    // 選択映画の傾向加味
    ratings.forEach(r => {
      if (selectedIds.includes(r.movieId)) {
        ratings
          .filter(x => x.userId === r.userId)
          .forEach(x => {
            if (!selectedIds.includes(x.movieId)) {
              scores[x.movieId] =
                (scores[x.movieId] || 0) + x.rating;
            }
          });
      }
    });
  }

  return Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([id]) => movies.find(m => m.movieId === id));
}

// ボタン処理
document.getElementById("recommendBtn").addEventListener("click", () => {
  const selected = [...document.querySelectorAll("input:checked")]
    .map(e => e.value);

  const result = document.getElementById("result");
  result.innerHTML = "";

  const recs = recommend(selected);
  recs.forEach(m => {
    const li = document.createElement("li");
    li.textContent = m.title;
    result.appendChild(li);
  });
});

init();
