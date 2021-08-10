from flask import Flask
from data import db_session, couriers_api
from flask import render_template, redirect, session
from forms.forms import PostCouriersForm, PostOrdersForm, PatchCouriersForm, AssignForm, CompleteForm,\
    RegisterForm, LoginForm, ExitForm, RegForm, SortingForm, FilterForm
from data.couriers import Couriers
from data.orders import Orders
from data.users import User
from requests import get, post, patch
from json import loads
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_secret_key'


@app.route('/post_couriers', methods=['GET', 'POST'])
def post_couriers():
    # Получение формы
    form = PostCouriersForm()
    if session.get('data'):
        name = session.get('data')['name']
    else:
        name = None

    # Проверка валидации формы
    if form.validate_on_submit():
        db_sess = db_session.create_session()  # Создание ссесии с БД

        # Получение данных из формы
        id = int(form.id.data)
        type = form.type.data
        regions = list(map(int, form.regions.data.split()))
        working_hours = form.working_hours.data.split()

        # Проверка наличия курьера с таким id
        if db_sess.query(Couriers).get(id):
            # Рендер страницы с сообщением об ошибке
            return render_template('post_couriers.html', title='Добавление курьера',
                                   form=form,
                                   message="Курьер с таким id уже существует", name=name)

        # POST запрос на добавления курьера
        post('http://localhost:8080/couriers',
             json={"data": [
                                {
                                    "courier_id": id, "courier_type": type, "regions": regions,
                                    "working_hours": working_hours
                                }
                            ]})

        email = session.get('data')['email']
        user = db_sess.query(User).filter(User.email == email).first()
        print(user)
        user.couriers_added += 1
        db_sess.commit()

        # Редирект на главную страницу
        return redirect('/')

    # Успешный рендер страницы
    return render_template('post_couriers.html', title='Добавление курьера', form=form, name=name)


@app.route('/post_orders', methods=['GET', 'POST'])
def post_orders():
    # Получение формы
    form = PostOrdersForm()
    if session.get('data'):
        name = session.get('data')['name']
    else:
        name = None

    # Проверка валидации формы
    if form.validate_on_submit():
        db_sess = db_session.create_session()  # Создание ссесии с БД

        # Получение данных из формы
        id = int(form.id.data)
        weight = float(form.weight.data)
        region = int(form.region.data)
        delivery_hours = form.delivery_hours.data.split()

        # Проверка наличия заказа с таким id
        if db_sess.query(Orders).get(id):
            # Рендер страницы с сообщением об ошибке
            return render_template('post_orders.html', title='Добавление заказа',
                                   form=form,
                                   message="Заказ с таким id уже существует", name=name)

        # POST запрос на добавления заказа
        post('http://localhost:8080/orders',
             json={
                     "data": [{
                         "order_id": id,
                         "weight": weight,
                         "region": region,
                         "delivery_hours": delivery_hours
                     }]
                })

        email = session.get('data')['email']
        user = db_sess.query(User).filter(User.email == email).first()
        user.orders_added += 1
        db_sess.commit()

        # Редирект на главную страницу
        return redirect('/')

    # Успешный рендер страницы
    return render_template('post_orders.html', title='Добавление заказа', form=form, name=name)


@app.route('/patch_couriers/<int:courier_id>', methods=['GET', 'PATCH', 'POST'])
def couriers(courier_id):
    # Получение форм
    form = PatchCouriersForm()
    assign_form = AssignForm()
    if session.get('data'):
        name = session.get('data')['name']
    else:
        name = None

    # GET запрос н получение данных курьера
    response = get('http://localhost:8080/couriers/' + str(courier_id))

    # Проверка успешности ответа
    if response.status_code == 400:
        # Рендер страницы с сообщением об ошибке
        return 'Не удалось получить данные курьера'

    db_sess = db_session.create_session()   # Создание ссесии с БД
    courier = db_sess.query(Couriers).get(loads(response.text.split('\n')[1])['courier_id'])

    # Проверка валидации формы
    if form.submit.data and form.validate():
        # Получение данных из формы
        type = form.type.data
        regions = list(map(int, form.regions.data.split()))
        working_hours = form.working_hours.data.split()

        # PATCH запрос на изменения курьера
        patch('http://localhost:8080/couriers/' + str(courier_id),
              json={
                  "courier_type": type,
                  "regions": regions,
                  "working_hours": working_hours
              })

        # Редирект на главную страницу
        return redirect('/')

    # Проверка валидации формы
    if assign_form.assign.data:
        # POST запрос на назначение заказов
        post('http://localhost:8080/orders/assign', json={
                        "courier_id": courier_id,
                    })

        # Редирект на главную страницу
        return redirect('/')

    # Успешный рендер страницы
    return render_template('patch_couriers.html', title='Изменение данных курьера',
                           data=loads(response.text.split('\n')[1]), form=form, assign_form=assign_form,
                           courier=courier, name=name)


@app.route('/get_orders/<int:order_id>', methods=['GET', 'POST'])
def orders(order_id):
    # Получение формы
    complete_form = CompleteForm()
    if session.get('data'):
        name = session.get('data')['name']
    else:
        name = None

    # GET запрос н получение данных заказа
    response = get('http://localhost:8080/orders/' + str(order_id))

    # Проверка успешности ответа
    if response.status_code == 400:
        # Рендер страницы с сообщением об ошибке
        return render_template('get_orders.html', title='Получение данных заказа',
                               message='Не удалось получить данные заказа', form=complete_form, name=name)

    # Получение json из ответа
    data = loads(response.text.split('\n')[1])

    # Проверка валидации формы
    if complete_form.validate_on_submit():
        # POST запрос на выполнение заказов
        post('http://localhost:8080/orders/complete',
             json={
                        "courier_id": data['courier_id'],
                        "order_id": order_id,
                        "complete_time": datetime.datetime.now().isoformat()[:-4] + 'Z'
                    })

        # Редирект на главную страницу
        return redirect('/')

    # Успешный рендер страницы
    return render_template('get_orders.html', title='Получение данных заказа',
                           data=data, form=complete_form, name=name)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    # Получение форм
    form = RegisterForm()
    if session.get('data'):
        name = session.get('data')['name']
    else:
        name = None

    # Проверка валидации формы
    if form.validate_on_submit():
        # Проверка повторного ввода пароля
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают", name=name)

        db_sess = db_session.create_session()   # Создание ссесии с БД

        # Проверка идентичности email адресса
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть", name=name)

        # Создание и добавление пользователя
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            couriers_added=0,
            orders_added=0
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        # Редирект на страницу авторизации
        return redirect('/login')

    # Успешный рендер страницы
    return render_template('register.html', title='Регистрация', form=form, name=name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Получение форм
    form = LoginForm()
    reg_form = RegForm()
    if session.get('data'):
        name = session.get('data')['name']
    else:
        name = None

    # Проверка валидации формы
    if form.submit.data and form.validate():

        db_sess = db_session.create_session()   # Создание ссесии с БД
        user = db_sess.query(User).filter(User.email == form.username.data).first()  # Получение юзера с данным email

        # Проверка существования такого пользователя
        if user:
            # Проверка пароля
            if user.check_password(form.password.data):
                session['data'] = dict(name=user.name, email=user.email)
                # Редирект на главную страницу
                return redirect('/')
            else:
                # Рендер страницы с сообщением об ошибке
                return render_template('login.html', title='Авторизация', form=form,
                                       message='Неверный пароль', name=name, form_register=reg_form)

        else:
            # Рендер страницы с сообщением об ошибке
            return render_template('login.html', title='Авторизация', form=form, message='Неверный логин',
                                   name=name, form_register=reg_form)

    # Проверка валидации формы
    if reg_form.reg.data:
        # Редирект на страницу регистрации
        return redirect('/register')

    # Успешный рендер страницы
    return render_template('login.html', title='Авторизация', form=form, name=name, form_register=reg_form)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Получение форм
    form = ExitForm()
    if session.get('data'):
        name = session.get('data')['name']
    else:
        name = None
    email = session.get('data')['email']

    db_sess = db_session.create_session()   # Создание ссесии с БД
    user = db_sess.query(User).filter(User.email == email).first()  # Получение юзера с данным email

    # Проверка валидации формы
    if form.validate_on_submit():
        session['data'] = dict(name='', email='')
        # Редирект на главную страницу
        return redirect('/')

    # Успешный рендер страницы
    return render_template('profile.html', title='Профиль', name=name, user=user, form=form)


@app.route('/', methods=['GET', 'POST'])
def main_pages():
    # Получение форм
    form = SortingForm()
    form_filter = FilterForm()
    if session.get('data'):
        name = session.get('data')['name']
    else:
        name = None

    db_sess = db_session.create_session()  # Создание ссесии с БД
    data = [db_sess.query(Couriers).all(), db_sess.query(Orders).all()]  # Сортировка и фильтрация поумолчанию

    # Проверка валидации формы
    if form.submit1.data and form.validate():
        # Сортировка по id
        if form.sorted_by.data == 'id':
            data[0] = db_sess.query(Couriers).all()

        # Сортировка по кол-ву выполненных заказов
        if form.sorted_by.data == 'По кол-ву выполненных заказов':
            data[0] = reversed(db_sess.query(Couriers).order_by(Couriers.delivery_count).all())

    # Проверка валидации формы
    if form_filter.submit2.data and form_filter.validate():
        # Вывод всех заказов
        if form_filter.filter_by.data == 'Все':
            data[1] = db_sess.query(Orders).all()

        # Фильтрация по свободности
        if form_filter.filter_by.data == 'Свободные':
            data[1] = db_sess.query(Orders).filter(Orders.is_available).all()

        # Фильтрация по занятости
        if form_filter.filter_by.data == 'Занятые':
            data[1] = db_sess.query(Orders).filter(Orders.courier_id).all()

        # Фильтрация по выполненности
        if form_filter.filter_by.data == 'Выполненные':
            data[1] = db_sess.query(Orders).filter(Orders.complete_by_id).all()

    # Успешный рендер страницы
    return render_template('main_page.html', title='Главная страница',
                           data=data, name=name, form1=form, form2=form_filter)


def main():
    db_session.global_init("sweet_store.db")    # Подключение к БД
    app.register_blueprint(couriers_api.blueprint)  # Подключение api
    app.run(port=8080, host='0.0.0.0')  # Запуск сервера


if __name__ == '__main__':
    main()
