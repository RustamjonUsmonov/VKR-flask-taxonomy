from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import enscript
import ruscript
from datetime import datetime
from langdetect import detect
import json
import secrets
import string
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

characters = string.ascii_letters + string.digits
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:254703rustam@localhost/taxonomies'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

Session = sessionmaker(bind=db.engine)
session = Session()


class Taxonomies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dictionaries = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<taxonomies {self.id}>"


class TaxonomyObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<taxonomies {self.id}>"


class TaxonomiesElement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    element = db.Column(db.Text)
    taxonomy_object_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<taxonomy_element {self.id}>"


class TaxonomiesRelations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    similarity = db.Column(db.Float)
    word_1_id = db.Column(db.Integer, db.ForeignKey(TaxonomiesElement.id), index=True)
    word_2_id = db.Column(db.Integer, db.ForeignKey(TaxonomiesElement.id), index=True)

    def __repr__(self):
        return f"<taxonomies_relation {self.id}>"


class TaxonomyNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    taxonomy_id = db.Column(db.Integer, db.ForeignKey(Taxonomies.id), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<taxonomy_notifications {self.id}>"


with app.app_context():
    db.create_all()


@app.route('/')
def home():  # put application's code here
    txt = """Natural language processing (NLP) is a field of computer science, artificial intelligence, 
        and computational linguistics concerned with the interactions between computers and human (natural) languages. """
    dict, counter = enscript.calculate_similarity(txt)
    return render_template('watch.html', dict=dict, counter=counter)


@app.route('/save-taxonomy', methods=["GET", "POST"])
def save_taxonomy():
    if request.method == "POST":
        try:
            txt = request.form['dictionaries']
            dict, counter = ruscript.calculate_similarity(txt) if is_ru(txt) else enscript.calculate_similarity(txt)
            t = Taxonomies(dictionaries=json.dumps(dict, ensure_ascii=False))
            db.session.add(t)
            db.session.flush()
            db.session.commit()

            n = TaxonomyNotification(taxonomy_id=t.id)
            db.session.add(n)
            db.session.commit()
            return render_template('watch.html', dict=dict, counter=counter)
        except:
            db.session.rollback()
            print('Error to store data in db')
    return render_template('test.html')


@app.route('/visualize')
def watch():
    txt = """

PostgreSQL is a powerful, open source object-relational database system with over 30 years of active development that has earned it a strong reputation for reliability, feature robustness, and performance.

There is a wealth of information to be found describing how to install and use PostgreSQL through the official documentation. The PostgreSQL community provides many helpful places to become familiar with the technology, discover how it works, and find career opportunities. Reach out to the community here.
 """
    dict, counter = enscript.calculate_similarity(txt)
    return render_template('watch.html', dict=dict, counter=counter)


def is_ru(txt):
    return detect(txt) == 'ru'


if __name__ == '__main__':
    app.run(debug=True)


def createObject():
    random_string = ''.join(secrets.choice(characters) for _ in range(12))
    me = TaxonomyObject(name=random_string)
    db.session.add(me)
    db.session.commit()
    return me.id


def saveTaxonomyElement(element, similarity, taxonomy_object_id, parent_id=None):
    record = TaxonomiesElement.query.filter_by(element=element).first()
    if (record is None):
        record = TaxonomiesElement(element=element, similarity=similarity,
                                   taxonomy_object_id=taxonomy_object_id, parent_id=parent_id)
        db.session.add(record)
        db.session.commit()
    else:
        record.element = element
        record.similarity = similarity
        record.taxonomy_object_id = taxonomy_object_id
        record.parent_id = parent_id
        db.session.commit()

    return record.id


def bulkInsertRelations(data):
    obj = session.query(TaxonomiesRelations).order_by(TaxonomiesRelations.id.desc()).first()
    records = []
    counter = obj.id + 1
    for item in data:
        records.append({'id': counter, 'word_1_id': item['word_1_id'], 'word_2_id': item['word_2_id'],
                        'similarity': item['similarity']})
        counter += 1

    session.bulk_insert_mappings(TaxonomiesRelations, data)
    session.commit()


def saveTaxonomyElements(data, taxonomy_object_id):
    counter = 1

    for item in data:
        record = TaxonomiesElement(id=counter, element=item, taxonomy_object_id=taxonomy_object_id)
        db.session.add(record)
        db.session.commit()
        counter += 1
