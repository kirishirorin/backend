from flask import Flask, flash, redirect, render_template, request, url_for
import os
from dotenv import load_dotenv
from backend.db import Database
from collections import namedtuple
from datetime import datetime, date


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/rolls/list')
def roll_list():
    data = request.form.to_dict()
    db = Database(DATABASE_URL)
    rolls = db.show()
    query = ''
    if data:
        if data['category'] == 'id' or data['category'] == 'length' or data['category'] == 'weight':
            query = int(data['query'])
        else:
            query = datetime.strptime(data['query'], '%d.%m.%Y').date()
        rolls = list(filter(lambda roll: roll[data['category']] == query, rolls))
    db.close_conn()
    return render_template('roll_list.html', rolls=rolls, search=query)

@app.get('/rolls/<id>')
def roll_select(id):
    db = Database(DATABASE_URL)
    roll = db.select(id)
    db.close_conn()
    return render_template('roll.html', roll=roll)


@app.get('/rolls/new')
def roll_new():
    #Roll = namedtuple("Roll", ['length', 'weight', 'created_at', 'deleted_at'])
    #roll = Roll(None, None, None, None)
    #errors = {}
    return render_template('new.html')


@app.post('/rolls')
def rolls_post():
    data = request.form.to_dict()
    db = Database(DATABASE_URL)
    db.insert(data)
    id = db.show_last_id()
    db.close_conn()
    flash('Рулон был успешно добавлен', 'success')
    return redirect(url_for('roll_select', id=id))


@app.get('/rolls/edit')
def roll_edit():
    return render_template('roll_patch.html')


@app.post('/rolls/patch')
def roll_patch():
    db = Database(DATABASE_URL)
    data = request.form.to_dict()
    id = int(data['id'])
    data['deleted_at'] = date.today()
    db.update(data)
    flash('Рулон был успешно удалён', 'success')
    return redirect(url_for('roll_select', id=id))
