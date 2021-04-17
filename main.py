from flask import Flask
from data import db_session, couriers_api
from flask import render_template, redirect
from forms.forms import PostCouriersForm, PostOrdersForm
from data.couriers import Couriers
from data.orders import Orders
from requests import get, post, patch


app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandex_secret_key'


@app.route('/post_couriers', methods=['GET', 'POST'])
def post_couriers():
    form = PostCouriersForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()  # Создание ссесии с БД

        id = int(form.id.data)
        type = form.type.data
        regions = list(map(int, form.regions.data.split()))
        working_hours = form.working_hours.data.split()

        if db_sess.query(Couriers).get(id):  # Получение курьера из БД
            return render_template('post_couriers.html', title='Добавление курьера',
                                   form=form,
                                   message="Курьер с таким id уже существует")

        print(post('http://localhost:8080/couriers',
                   json={"data": [
                                    {
                                        "courier_id": id, "courier_type": type, "regions": regions,
                                        "working_hours": working_hours
                                    }
                                 ]}).text)

        return redirect('/')
    return render_template('post_couriers.html', title='Добавление курьера', form=form)


@app.route('/post_orders', methods=['GET', 'POST'])
def post_orders():
    form = PostOrdersForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()  # Создание ссесии с БД

        id = int(form.id.data)
        weight = float(form.weight.data)
        region = int(form.region.data)
        delivery_hours = form.delivery_hours.data.split()

        if db_sess.query(Orders).get(id):  # Получение заказа из БД
            return render_template('post_orders.html', title='Добавление заказа',
                                   form=form,
                                   message="Заказ с таким id уже существует")

        print(post('http://localhost:8080/orders',
              json={
                 "data": [{
                     "order_id": id,
                     "weight": weight,
                     "region": region,
                     "delivery_hours": delivery_hours
                 }]
             }).text)

        return redirect('/')
    return render_template('post_orders.html', title='Добавление заказа', form=form)


@app.route('/', methods=['GET'])
def main_pages():
    db_sess = db_session.create_session()  # Создание ссесии с БД
    return render_template('main_page.html', title='fd', data=[db_sess.query(Couriers).all(),
                                                               db_sess.query(Orders).all()])


def main():
    db_session.global_init("sweet_store.db")    # Подключение к БД
    app.register_blueprint(couriers_api.blueprint)  # Подключение api
    app.run(port=8080, host='0.0.0.0')  # Запуск сервера


if __name__ == '__main__':
    main()
