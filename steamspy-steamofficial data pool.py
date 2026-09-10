import requests
import json


# ambil data basic dari 2 api berdasarkan genre&tag indie
print("Fetching genre=Indie pool..")
url_genre = "https://steamspy.com/api.php?request=genre&genre=Indie"
genre_response = requests.get(url_genre)
genre_data = genre_response.json()
print(f" Got {len(genre_data)} games")

print("Fetching genre=Indie pool..")
url_genre = "https://steamspy.com/api.php?request=tag&tag=Indie"
tag_response = requests.get(url_genre)
tag_data = tag_response.json()
print(f" Got {len(tag_data)} games")


# save data json ke komputer:
with open("[genre]steamspy_pool.json", "w") as f:
    json.dump(genre_data, f)

with open("[tag]steamspy_pool.json", "r") as f:
    json.dump(tag_data, f)

print("Data Pool Saved")