import os
from flask import Flask, jsonify, request
from deepface import DeepFace
import pandas as pd
import random
import numpy as np
import cv2



app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = 'static/uploads/'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route("/")
def index():
    return jsonify({
        "status": {
            "code": 200,
            "message": "Success fetching the API"
        }
    }), 200

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        image = request.files["image"]
        if image and allowed_file(image.filename):
            image_bytes = image.read()

            # Convert image bytes to image array using cv2
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            result = DeepFace.analyze(img, actions=['age', 'gender', 'race', 'emotion'])
            print(result)
            print("================")
            print(result[0]["dominant_gender"])
            print(result[0]["dominant_race"])
            print("================")

            # Recommendation
            race = result[0]["dominant_race"]
            gender = result[0]["dominant_gender"]

            outfits = []
            df = pd.read_csv("data.csv")
            df_recommendation = df[(df["race"] == race) & (df["gender"] == gender)]
            print(df_recommendation)

            if not df_recommendation.empty:
                for index, row in df_recommendation.iterrows():
                    items = row["rekomendasi"].split(", ")
                    images = row["gambar"].split(", ")
                    price = row["price"].split(", ")
                    style = row["style"]
                    outfits.append((items, images, style, price))
                    
            
            # Randomly select one outfit
            random_outfit = random.choice(outfits)
            items, images, style, price = random_outfit

            # Add prefix to each image filename
            image_urls = ["https://storage.googleapis.com/mixmate/" + image for image in images]

            outfit_list = []
            for i in range(len(items)):
                outfit = {
                    "images": image_urls[i],
                    "item_name": items[i],
                    "price": price[i]
                }
                outfit_list.append(outfit)

            return jsonify({
                "gender": gender,
                "race": race,
                "outfits": outfit_list,
                "style": style
            })


        else:
            return jsonify({
                "status": {
                    "code": 400,
                    "message": "Please upload image with JPG format"
                }
            }), 400
    else:
        return jsonify({
            "status": {
                "code": 405,
                "message": "Method not allowed"
            }
        }), 405


if __name__ == "__main__":
    app.run()