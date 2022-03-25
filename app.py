from flask import Flask, render_template
import script

app = Flask(__name__)


@app.route('/')
def home():  # put application's code here
    dict, counter = script.calculate_similarity()
    return render_template('index.html', dict=dict, counter=counter)


if __name__ == '__main__':
    app.run(debug=True)
