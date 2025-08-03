from flask import Flask
from flask import render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration')
def registration():
    return render_template('user_reg_form.html')

@app.route('/result', methods=['POST'])
def result():
    username = request.form['username']
    return render_template('user_reg_result.html', username=username)