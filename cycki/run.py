import os

from flask import Flask, render_template

'''
ExamIT - Multiple-choice Test Correction Utility
Created by Roger Marciniak
IT Carlow 2017
'''


app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',
                           title="Home")


@app.route("/questions")
def questions():
    return render_template('questions.html',
                           title="Questions")


@app.route("/addquestion")
def add_question():
    return render_template('qadd.html',
                           title="Add Question")


@app.route("/tests")
def tests():
    return render_template('tests.html',
                           title="Tests")


@app.route("/addtest")
def add_test():
    return render_template('tadd.html',
                           title="Add Test")


@app.errorhandler(404)
def fourOhFour(error):
    return render_template('404.html',
                           title="404")


app.secret_key = os.urandom(32)


if __name__ == '__main__':
    app.run(debug=True)
