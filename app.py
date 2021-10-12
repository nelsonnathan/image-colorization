from flask import Flask, render_template, request 
import boto3
from werkzeug.utils import secure_filename
import key_configuration as keys

app = Flask(__name__)

s3 = boto3.client('s3', aws_access_key_id=keys.ACCESS_KEY_ID,
                        aws_secret_access_key=keys.ACCESS_SECRET_KEY)


BUCKET_NAME = 'colorization-capstone'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        img = request.files['file']
        if img:
            filename = secure_filename(img.filename)
            img.save(filename)
            s3.upload_file(
                Bucket = BUCKET_NAME,
                Filename = filename, 
                Key = filename
            )
            message = 'Successfully uploaded!'

    return render_template('index.html', message=message)


if __name__ == "__main__":
    app.run(debug=True)