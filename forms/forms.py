from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField, DateField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, AnyOf
from data.tools import type_is_integer, type_is_float, region_validation, working_hours_validation


# Форма для добавления курьеров
class PostCouriersForm(FlaskForm):
    id = StringField('id курьера', validators=[DataRequired(), type_is_integer])
    type = StringField('Тип курьера', validators=[DataRequired(), AnyOf(('foot', 'bike', 'car'))])
    regions = StringField('Регионы работы(вводить через пробел)', validators=[DataRequired(), region_validation])
    working_hours = StringField('Времена работы(вводить через пробел)', validators=[DataRequired(),
                                                                                    working_hours_validation])
    submit = SubmitField('Добавить')


# Форма для добавления заказов
class PostOrdersForm(FlaskForm):
    id = StringField('id заказа', validators=[DataRequired(), type_is_integer])
    weight = StringField('Вес заказа', validators=[DataRequired(), type_is_float])
    region = StringField('Регион доставки', validators=[DataRequired(), type_is_integer])
    delivery_hours = StringField('Время Доставки', validators=[DataRequired(),
                                                               working_hours_validation])
    submit = SubmitField('Добавить')


# Форма для изменения данных курьера
class PatchCouriersForm(FlaskForm):
    type = StringField('Тип курьера', validators=[DataRequired(), AnyOf(('foot', 'bike', 'car'))])
    regions = StringField('Регионы работы(вводить через пробел,',
                          validators=[DataRequired(), region_validation])
    working_hours = StringField('Времена работы(вводить через пробел,', validators=[DataRequired(),
                                                                                    working_hours_validation])
    submit = SubmitField('Изменить')


# Форма для назначения зказов
class AssignForm(FlaskForm):
    assign = SubmitField('Назначить заказы')


# Форма для выполнения заказов
class CompleteForm(FlaskForm):
    submit = SubmitField('Завершить заказ')


# Форма для выхода из профиля
class ExitForm(FlaskForm):
    submit = SubmitField('Выйти')


# Форма для перехода на страницу для регистрации
class RegForm(FlaskForm):
    reg = SubmitField('Зарегистрироваться')


# Форма регистрации
class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


# Форма авторизации
class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


# Форма для сортировки курьеров
class SortingForm(FlaskForm):
    choice_list = ['id', 'По кол-ву выполненных заказов']
    sorted_by = SelectField('Сортировать по:', choices=choice_list)
    submit1 = SubmitField('Сортировать')


# Форма для фильтрации курьеров
class FilterForm(FlaskForm):
    choice_list = ['Все', 'Свободные', 'Занятые', 'Выполненные']
    filter_by = SelectField('Сортировать по:', choices=choice_list)
    submit2 = SubmitField('Сортировать')