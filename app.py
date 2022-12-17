#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, url_for, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer, PrimaryKeyConstraint, String, func
from sqlalchemy.orm import relationship

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///nom.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Informant(db.Model):
    __tablename__ = "users"
    informant_id = db.Column("user_id", db.Integer, primary_key = True)
    infgender = db.Column("gender", db.Text)
    infage = db.Column("age", db.Integer)
    
    answers = db.relationship("Question", secondary = "answers")

class Question(db.Model):
    __tablename__ = "questions"
    question_id = db.Column("q_id", db.Integer, primary_key = True)
    question = db.Column("q_text", db.Text)
    
class Answer(db.Model):
    __tablename__ = "answers"
    __table_args__ = (PrimaryKeyConstraint("user_id", "q_id"),)
    
    informant_id = db.Column("user_id", db.Integer, ForeignKey("users.user_id"))
    question_id = db.Column("q_id", db.Integer, ForeignKey("questions.q_id"))
    answer = db.Column("answer", db.Integer)

@app.before_first_request
def create_tables():
    db.create_all()    
    
@app.route("/")
def index():
    return render_template("myindex.html")

@app.route("/form/", methods = ["get"])
def form():
    if not request.args:
        return render_template("form.html")
    
    ugender = request.args.get("gender")
    uage = request.args.get("age")
    
    user = Informant(infgender = ugender, infage = uage)
    db.session.add(user)
    db.session.commit()
    
    db.session.refresh(user)
    q1 = request.args.get("q1")
    q2 = request.args.get("q2")
    q3 = request.args.get("q3")
    q4 = request.args.get("q4")
    answer1 = Answer(informant_id = user.informant_id, question_id = 1, answer=q1)
    answer2 = Answer(informant_id = user.informant_id, question_id = 2, answer=q2)
    answer3 = Answer(informant_id = user.informant_id, question_id = 3, answer=q3)
    answer4 = Answer(informant_id = user.informant_id, question_id = 4, answer=q4)
    db.session.add(answer1)
    db.session.add(answer2)
    db.session.add(answer3)
    db.session.add(answer4)
    db.session.commit()
    
    return render_template("form.html")

@app.route("/stats/")
def stats():
    all_info = {}
    age_stats = db.session.query(
        func.avg(Informant.infage),
        func.min(Informant.infage),
        func.max(Informant.infage)
    ).one()
    all_info["age_mean"] = age_stats[0]
    all_info["age_min"] = age_stats[1]
    all_info["age_max"] = age_stats[2]
    all_info["total_count"] = Informant.query.count()
    all_info["f"] = Informant.query.filter(Informant.infgender == "ж").count()
    all_info["m"] = Informant.query.filter(Informant.infgender == "м").count()
    all_info["q1_mean"] = db.session.query(func.avg(Answer.answer)).filter(Answer.question_id == 1).one()[0]
    all_info["q2_mean"] = db.session.query(func.avg(Answer.answer)).filter(Answer.question_id == 2).one()[0]
    all_info["q3_mean"] = db.session.query(func.avg(Answer.answer)).filter(Answer.question_id == 3).one()[0]
    all_info["q4_mean"] = db.session.query(func.avg(Answer.answer)).filter(Answer.question_id == 4).one()[0]
    return render_template("stats.html", all_info = all_info)

if __name__ == "__main__":
    app.run(debug = False)

