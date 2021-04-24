from flask import Flask
from data import db_session, couriers_api
from flask import render_template, redirect
from forms.forms import PostCouriersForm, PostOrdersForm, PatchCouriersForm, AssignForm, CompleteForm
from data.couriers import Couriers
from data.orders import Orders
from requests import get, post, patch
from json import loads
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_secret_key'


@app.route('/post_couriers', methods=['GET', 'POST'])
def post_couriers():
    # Получение формы
    form = PostCouriersForm()

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
                                   message="Курьер с таким id уже существует")

        # POST запрос на добавления курьера
        post('http://localhost:8080/couriers',
             json={"data": [
                                {
                                    "courier_id": id, "courier_type": type, "regions": regions,
                                    "working_hours": working_hours
                                }
                            ]})

        # Редирект на главную страницу
        return redirect('/')

    # Успешный рендер страницы
    return render_template('post_couriers.html', title='Добавление курьера', form=form)


@app.route('/post_orders', methods=['GET', 'POST'])
def post_orders():
    # Получение формы
    form = PostOrdersForm()

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
                                   message="Заказ с таким id уже существует")

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

        # Редирект на главную страницу
        return redirect('/')

    # Успешный рендер страницы
    return render_template('post_orders.html', title='Добавление заказа', form=form)


@app.route('/patch_couriers/<int:courier_id>', methods=['GET', 'PATCH', 'POST'])
def couriers(courier_id):
    # Получение форм
    form = PatchCouriersForm()
    assign_form = AssignForm()

    # GET запрос н получение данных курьера
    response = get('http://localhost:8080/couriers/' + str(courier_id))

    db_sess = db_session.create_session()   # Создание ссесии с БД
    courier = db_sess.query(Couriers).get(loads(response.text.split('\n')[1])['courier_id'])

    # Проверка успешности ответа
    if response.status_code == 400:
        # Рендер страницы с сообщением об ошибке
        return render_template('patch_couriers.html', title='Изменение данных курьера',
                               message='Не удалось получить данные курьера', form=form, assign_form=assign_form)

    # Проверка валидации формы
    if form.validate_on_submit():
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
    if assign_form.validate_on_submit():
        # POST запрос на назначение заказов
        post('http://localhost:8080/orders/assign', json={
                        "courier_id": courier_id,
                    })

        # Редирект на главную страницу
        return redirect('/')

    # Успешный рендер страницы
    return render_template('patch_couriers.html', title='Изменение данных курьера',
                           data=loads(response.text.split('\n')[1]), form=form, assign_form=assign_form,
                           courier=courier)


@app.route('/get_orders/<int:order_id>', methods=['GET', 'POST'])
def orders(order_id):
    # Получение форм
    complete_form = CompleteForm()

    # GET запрос н получение данных заказа
    response = get('http://localhost:8080/orders/' + str(order_id))

    # Проверка успешности ответа
    if response.status_code == 400:
        return render_template('get_orders.html', title='Получение данных заказа',
                               message='Не удалось получить данные заказа', form=complete_form)

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
                           data=data, form=complete_form)


@app.route('/', methods=['GET'])
def main_pages():
    db_sess = db_session.create_session()  # Создание ссесии с БД

    # Успешный рендер страницы
    return render_template('main_page.html', title='Главная страница', data=[db_sess.query(Couriers).all(),
                                                                             db_sess.query(Orders).all()])


def main():
    db_session.global_init("sweet_store.db")    # Подключение к БД
    app.register_blueprint(couriers_api.blueprint)  # Подключение api
    app.run(port=8080, host='0.0.0.0')  # Запуск сервера


if __name__ == '__main__':
    main()
