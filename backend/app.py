import os
from datetime import date, datetime, timedelta
from statistics import mean

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from pydantic import BaseModel, Field, field_validator

from backend.db import Database

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


class ID(BaseModel):
    id: int

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, int):
            return v
        elif isinstance(v, str):
            return int(v)
        else:
            raise ValueError("id должен быть числом")


class Roll(BaseModel):
    length: int
    weight: int
    created_at: date = Field(default=date.today())
    deleted_at: date = Field(default=None)

    @field_validator('length', mode='before')
    @classmethod
    def validate_length(cls, v):
        if isinstance(v, int):
            return v
        elif isinstance(v, str):
            return int(v)
        else:
            raise ValueError("Длина должна быть числом")

    @field_validator('weight', mode='before')
    @classmethod
    def validate_weight(cls, v):
        if isinstance(v, int):
            return v
        elif isinstance(v, str):
            return int(v)
        else:
            raise ValueError("Вес должен быть числом")

    @field_validator('created_at', mode='before')
    @classmethod
    def validate_created_at(cls, v):
        if isinstance(v, date):
            return v
        elif isinstance(v, str):
            return datetime.strptime(v, '%d.%m.%Y').date()
        else:
            raise ValueError("Дата создания должена быть датой")

    @field_validator('deleted_at', mode='after')
    @classmethod
    def validate_deleted_at(cls, v):
        if v is None:
            return v
        elif isinstance(v, str):
            return datetime.strptime(v, '%d.%m.%Y').date()
        elif isinstance(v, date):
            return v
        else:
            raise ValueError("Дата удаления должена быть датой")


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
        if (data['category'] == 'id'
            or data['category'] == 'length' or data['category'] == 'weight'):
            query = int(data['query'])
        else:
            query = datetime.strptime(data['query'], '%d.%m.%Y').date()
        rolls = list(filter(
                     lambda roll: roll[data['category']] == query, rolls))
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
    return render_template('new.html')


@app.post('/rolls')
def roll_post():
    data = request.form.to_dict()
    correct_data = Roll(length=data['length'],
                        weight=data['weight']).model_dump()
    db = Database(DATABASE_URL)
    db.insert(correct_data)
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
    id = ID(id=data['id']).model_dump()
    if not db.select(id['id']):
        flash('Такой id не существует', 'danger')
        return redirect(url_for('roll_edit')), 422
    elif db.select(id['id'])['deleted_at']:
        flash('Дата удаления уже есть', 'warning')
        return redirect(url_for('roll_edit')), 422
    roll = db.select(id['id'])
    correct_data = Roll(length=roll['length'],
                        weight=roll['weight'],
                        created_at=roll['created_at'],
                        deleted_at=date.today()).model_dump()
    correct_data.update(id)
    db.update(correct_data)
    db.close_conn()
    flash('Рулон был успешно удалён', 'success')
    return redirect(url_for('roll_select', id=id['id']))


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
    filter_data = list(filter(lambda roll: roll['created_at'] >= start_date
                              and roll['created_at'] <= end_date, rolls))
    filter_data_deleted = list(filter(
                               lambda roll: roll['deleted_at'], filter_data))
    dates_list = []
    for n in range(int((end_date - start_date).days)):
        d = start_date + timedelta(n)
        count = len(list(filter(lambda roll: d >= roll['created_at']
                                and d < roll['deleted_at'] if roll['deleted_at']
                                else d >= roll['created_at'], filter_data)))
        dates_list.append({'date': d, 'count': count})
    count_created = len(filter_data)
    count_deleted = len(filter_data_deleted)
    avg_length = round(mean(list(map(lambda roll: roll['length'],
                                     filter_data))), 2)
    avg_weight = round(mean(list(map(
                       lambda roll: roll['weight'], filter_data))), 2)
    max_length = max(list(map(
                     lambda roll: roll['length'], filter_data)))
    min_length = min(list(map(
                     lambda roll: roll['length'], filter_data)))
    max_weight = max(list(map(
                     lambda roll: roll['weight'], filter_data)))
    min_weight = min(list(map(
                     lambda roll: roll['weight'],
                     filter_data)))
    sum_weight = sum(list(map(
                     lambda roll: roll['weight'],
                     filter_data)))
    max_delta = max(list(map(
                    lambda roll: (roll['deleted_at'] - roll['created_at']),
                         filter_data_deleted)))
    min_delta = min(list(map(
                    lambda roll: (roll['deleted_at'] - roll['created_at']),
                             filter_data_deleted)))
    date_with_max_count = list(filter(lambda elem: elem['count'] == max(
                               list(map(lambda elem: elem['count'],
                                      dates_list))), dates_list))
    date_with_min_count = list(filter(lambda elem: elem['count'] == min(list(
                                      map(lambda elem: elem['count'],
                                      dates_list))), dates_list))
    info = {'start_date': start_date, 'end_date': end_date,
            'count_created': count_created, 'count_deleted': count_deleted,
            'avg_length': avg_length, 'avg_weight': avg_weight,
            'max_length': max_length, 'min_length': min_length,
            'max_weight': max_weight, 'min_weight': min_weight,
            'sum_weight': sum_weight,
            'max_delta': max_delta, 'min_delta': min_delta,
            'date_with_max_count': date_with_max_count,
            'date_with_min_count': date_with_min_count}
    db.close_conn()
    return render_template('roll_info_show.html', info=info)


@app.errorhandler(500)
def page_has_problem(e):
    return render_template('500.html'), 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
