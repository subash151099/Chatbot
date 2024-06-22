from flask import Flask, render_template, request, jsonify


app = Flask(__name__)

responses = {
    "hi": "Hello I am Subash! How can I help you?",
    "how are you": "I'm fine, thank you! How about you?",
    "bye": "Goodbye! Take care.",
    "820": "Check Supporting Document Type",
    "349": "COO Mismatching"
}

# Default response when no keyword matches
default_response = "I'm sorry, I didn't understand that."

# Function to get response based on keywords
def get_response(message):
    message = message.lower()
    for key in responses:
        if key in message:
            return responses[key]
    return default_response


@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    return get_response(input)


if __name__ == '__main__':
    app.run(debug=True)
