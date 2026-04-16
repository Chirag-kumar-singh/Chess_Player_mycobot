from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Image Viewer</h1><img src='/warped'>"

@app.route('/image_view')
def warped():
    return send_file("warped.jpg", mimetype='image/jpeg')

if __name__ == "__main__":
    print("Starting server...")
    app.run(host='0.0.0.0', port=5001)
