import numpy as np
import pandas as pd

from scipy.sparse import csr_matrix # ①
from sklearn.neighbors import NearestNeighbors 


df = pd.read_csv("./ratings_100k.csv", sep=",") # ①
df = df.iloc[:,0:3] # ②
df

df_movies = pd.read_csv("./movies_100k.csv", sep="|") # ①
df_movies

df_piv = df.pivot(
index= "movieId",
columns="userId",
values="rating"
).fillna(0) # ③
df_sp = csr_matrix(df_piv.values)

rec = NearestNeighbors(
n_neighbors=11,
algorithm= "brute",
metric= "cosine"
) # ⑤
rec_model = rec.fit(df_sp)

def recommend_movie_by_id(movies, movie_id):
    try:
        target_index = movies[movies['movie_id'] == movie_id].index[0]
        distance, indice = rec_model.kneighbors(
            df_piv.iloc[df_piv.index==target_index+1].values.reshape(1,-1),
            n_neighbors=11,
        )
        for i in range(11):
            if i == 0:
                movie_title = df_movies.loc[target_index, 'movie_title']
                message = 'を見た人におすすめの映画は以下の通りです。'
                result_sentence = f'{movie_title}{message}'
            else:
                target_index = indice.flatten()[i]
                piv_index = df_piv.index[target_index]
                movie_title = df_movies.loc[piv_index, 'movie_title']
                result_sentence += f'\n{i}: {movie_title}'
        return result_sentence  # ← ループの外に移動
    except IndexError:
        result_sentence = '入力されたIDは検索候補には存在しません。'
        result_sentence += '再度確認して入力をしてください。'
        return result_sentence

# 実行
## pd.read_csvを使って、映画の評価データを読み込み
df = pd.read_csv("./ratings_100k.csv", sep=",")
## ilocを使って、ID、映画ID、評価の3列までのデータを抽出
df = df.iloc[:,0:3]
## pd.read_csvを使って、映画のデータを読み込み
df_movies = pd.read_csv("./movies_100k.csv", sep="|")
## df.pivotを使ってデータフレームを作成
## 映画IDをインデックス、ユーザーIDをカラム、評価値を値に設定
## fillna(0)を使って、欠損値を0で埋める
df_piv = df.pivot(index="movieId",columns="userId",values="rating").fillna(0)
## csr_matrixを使って、データフレームを疎行列に変換
df_sp = csr_matrix(df_piv.values)
## NearestNeighborsを使って、類似度を計算するためのモデルを作成
## 近傍点の数を11、アルゴリズムをbrute、距離尺度をcosineに設定
rec = NearestNeighbors(n_neighbors=11,algorithm="brute", metric="cosine")
## fitメソッドを使って、モデルを学習
rec_model = rec.fit(df_sp)

result = recommend_movie_by_id(df_movies, 50)
print(result)