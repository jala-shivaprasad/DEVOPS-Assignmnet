from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>DevOps Assignment</h1>
    <h2>Application Successfully Deployed</h2>
    <p>AWS EC2 + Docker + Jenkins + Nginx</p>
    """

@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "application": "DevOps Assignment"
    })

@app.route("/about")
def about():
    return jsonify({
        "developer": "Your Name",
        "deployment": "AWS EC2",
        "container": "Docker",
        "ci_cd": "Jenkins"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
