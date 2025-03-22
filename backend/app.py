from flask import Flask, flash, redirect, render_template, request, url_for
import os
from dotenv import load_dotenv
from backend.db import Database
from collections import namedtuple
from datetime import datetime, date
from statistics import mean


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/rolls/list')
def roll_list():
    data = request.args
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
def roll_post():
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
    db.close_conn()
    flash('Рулон был успешно удалён', 'success')
    return redirect(url_for('roll_select', id=id))



@app.get('/rolls/info')
def roll_info():
    return render_template('roll_info.html')


@app.get('/rolls/info/show')
def roll_info_show():
    data = request.args
    db = Database(DATABASE_URL)
    rolls = db.show()
    start_date = datetime.strptime(data['start_period'], '%d.%m.%Y').date()
    end_date = datetime.strptime(data['end_period'], '%d.%m.%Y').date()
    filter_data = list(filter(lambda roll: roll.created_at >= start_date and roll.created_at <= end_date, rolls))
    filter_data_deleted = list(filter(lambda roll: roll.deleted_at, filter_data))
    count_created = len(filter_data)
    count_deleted = len(filter_data_deleted)
    avg_length = round(mean(list(map(lambda roll: roll.length, filter_data))), 2)
    avg_weight = round(mean(list(map(lambda roll: roll.weight, filter_data))), 2)
    max_length = max(list(map(lambda roll: roll.length, filter_data)))
    min_length = min(list(map(lambda roll: roll.length, filter_data)))
    max_weight = max(list(map(lambda roll: roll.weight, filter_data)))
    min_weight = min(list(map(lambda roll: roll.weight, filter_data)))
    sum_weight = sum(list(map(lambda roll: roll.weight, filter_data)))
    max_delta = max(list(map(lambda roll: (roll.deleted_at - roll.created_at), filter_data_deleted)))
    min_delta = min(list(map(lambda roll: (roll.deleted_at - roll.created_at), filter_data_deleted)))
    info = {'start_date': start_date, 'end_date': end_date,
            'count_created': count_created, 'count_deleted': count_deleted,
            'avg_length': avg_length, 'avg_weight': avg_weight,
            'max_length': max_length, 'min_length': min_length,
            'max_weight': max_weight, 'min_weight': min_weight,
            'sum_weight': sum_weight,
            'max_delta': max_delta, 'min_delta': min_delta}
    db.close_conn()
    return render_template('roll_info_show.html', info=info)
