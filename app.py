from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import script
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:254703rustam@localhost/taxonomies'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Taxonomies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dictionaries = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<taxonomies {self.id}>"


@app.route('/')
def home():  # put application's code here
    dict, counter = script.calculate_similarity()
    return render_template('index.html', dict=dict, counter=counter)


@app.route('/save-taxonomy', methods=["GET", "POST"])
def save_taxonomy():
    if request.method == "POST":
        try:
            t = Taxonomies(dictionaries=request.form['dictionaries'])
            db.session.add(t)
            db.session.flush()
            db.session.commit()
        except:
            db.session.rollback()
            print('Error to store data in db')
    return render_template('test.html')


@app.route('/visualize')
def watch():
    dict, counter = script.calculate_similarity()
    return render_template('watch.html', dict=dict, counter=counter)


if __name__ == '__main__':
    app.run(debug=True)
