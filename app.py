import os
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from deepface import DeepFace



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
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            result = DeepFace.analyze(image_path, actions=['age', 'gender', 'race', 'emotion'])
            print("Race:", result['dominant_race'])
            return result
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