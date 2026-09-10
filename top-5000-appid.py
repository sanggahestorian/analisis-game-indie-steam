import json 
import math
import pandas as pd

with open("[tag]steamspy_pool.json", "r") as f:
    tag_data = json.load(f)

with open("[genre]steamspy_pool.json", "r") as f:
    genre_data = json.load(f)


# kombinasikan dan deduplikasi 2 pool data yang sudah difetch pakai key appid:
combined = {**tag_data, **genre_data}
print(f"\nCombined (deduped): {len(combined)} games")
 
df = pd.DataFrame(list(combined.values()))

#filter game yang memiliki <10 review agar tidak masuk dalam kalkulasi wilson dibawah
df["total_reviews"] = df["positive"] + df["negative"]
filtered_games = df[df["total_reviews"] >= 10].copy()
print(f"Games with 10+ reviews: {len(filtered_games)} games")


# Pakai rumus wilson lower bound untuk mengestimasi rasio positif 
# memberi nilai tinggi pada game dengna persentase ulasan positif yang konsisten
# agar game dengan sampel kecil, misalnya 30 ulasan sempurna, mengalahkan ranking game dengan 1000 ulasan bagus tapi 100 ulasan negatif


def wilson_lower_bound(successes, n, confidence=0.95):
    if n == 0:
        return 0.0

    from scipy.stats import norm
    z = norm.ppf(1 - (1 - confidence) / 2)

    p_hat = successes / n
    denom = 1 + z**2 / n
    center = p_hat + z**2 / (2 * n)
    margin = z * math.sqrt((p_hat * (1 - p_hat) / n) + (z**2 / (4 * n**2)))

    return max(0.0, (center - margin) / denom)

filtered_games["positive_ratio"] = filtered_games["positive"] / filtered_games["total_reviews"]
filtered_games["wilson_score"] = filtered_games.apply(
lambda row: wilson_lower_bound(row["positive"], row["total_reviews"]), axis=1
)

# 2 baris ini mengubah total_reviews dan wilson_score jadi peringkat. rank 1 = terbaik, dst
# maka dari itu, harus dilakukan sorting descending dengan cara .rank(ascending=False)
filtered_games["popularity_rank"] = filtered_games["total_reviews"].rank(ascending=False)
filtered_games["quality_rank"] = filtered_games["wilson_score"].rank(ascending=False)


# mengkombinasikan cara ranking: popularitas dan kualitas, berdasarkan variabel 2 baris diatas. 
# metode ini merata-ratakan kedua variabel (popularitas dan kulaitas) dengan bobot 50-50
filtered_games["blended_rank"] = (filtered_games["popularity_rank"] + filtered_games["quality_rank"]) / 2


# urutkan game berdasarkan blended_rank dan ambil 5000 baris teratas sebagai sampel
top_5000 = filtered_games.sort_values("blended_rank", ascending=True).head(5000)

# Ambil semua value dari kolom 'appid' dan simpan sebagai file .json
top_5000_appids = top_5000["appid"].tolist()
with open("[wilson_rank]top_5000_appids.json", "w") as f:
    json.dump(top_5000_appids, f)

# simpan data appid sebagai file .csv untuk pemakaian 
top_5000.to_csv("[wilson_rank]top_5000_appids.csv", index=False)


print(f"\nSaved top {len(top_5000_appids)} appids (50/50 popularity+quality rank)")
print("\nTop 15 by blended rank:")
# cek 15 game pertama dari tabel, tampilkan value dari kolom-kolom yang dicantumkan dibaris bawah:
print(top_5000[["name", "positive", "negative", "total_reviews", "wilson_score", "blended_rank"]].head(15).to_string())
