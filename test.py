from requests import get, post, patch
import datetime

# Проверка валидации данных post запроса курьеров
print('----------------------------------------------------------')


def post_couriers():
    print(post('http://localhost:8080/couriers',
               json={
                    "data":[
                            {
                                "courier_id": 7, "courier_type": "car", "regions": [9],
                                "working_hours": ["09:00-18:00"]
                            }
                    ]}).text)
    print(post('http://localhost:8080/couriers',
               json={
                    "data":[
                            {
                                "courier_id": '', "courier_type": "car", "regions": [9],
                                "working_hours": ["09:00-18:00"]
                            }
                    ]}).text)
    print(post('http://localhost:8080/couriers',
               json={
                    "data":[
                            {
                                "courier_id": 7, "courier_type": 1, "regions": [9],
                                "working_hours": ["09:00-18:00"]
                            }
                    ]}).text)
    print(post('http://localhost:8080/couriers',
               json={
                    "data":[
                            {
                                "courier_id": 7, "courier_type": "car", "regions": [],
                                "working_hours": ["09:00-18:00"]
                            }
                    ]}).text)
    print(post('http://localhost:8080/couriers',
               json={
                    "data":[
                            {
                                "courier_id": 7, "courier_type": "car", "regions": [9],
                            }
                    ]}).text)


post_couriers()


print('----------------------------------------------------------')

# Проверка валидации данных patch запроса курьеров
print('----------------------------------------------------------')


def patch_couriers():
    print(patch('http://localhost:8080/couriers/7',
                json={
                        "courier_type": "bike",
                        "regions": [9, 11, 10],
                        "working_hours": ["08:00-18:00"]
                    }).text)
    print(patch('http://localhost:8080/couriers/7',
                json={
                        "courier_type": "",
                        "regions": [9, 11, 10],
                        "working_hours": ["08:00-18:00"]
                    }).text)
    print(patch('http://localhost:8080/couriers/7',
                json={
                        "courier_type": "bike",
                        "regions": [],
                        "working_hours": ["08:00-18:00"]
                    }).text)
    print(patch('http://localhost:8080/couriers/7',
                json={
                        "courier_type": "bike",
                        "regions": [9, 11, 10],
                        "working_hours": []
                    }).text)
    print(patch('http://localhost:8080/couriers/7',
                json={
                        "courier_id": 1,
                        "courier_type": "bike",
                        "regions": [9, 11, 10],
                        "working_hours": []
                }).text)


patch_couriers()


print('----------------------------------------------------------')

# Проверка валидации данных post запроса заказов
print('----------------------------------------------------------')


def post_orders():
    print(post('http://localhost:8080/orders',
               json={
                "data": [{
                        "order_id": 22,
                        "weight": 2,
                        "region": 11,
                        "delivery_hours": ["08:00-18:00"]
                        }]
                }).text)
    print(post('http://localhost:8080/orders',
               json={
                "data": [{
                        "order_id": '',
                        "weight": 17,
                        "region": 11,
                        "delivery_hours": ["08:00-18:00"]
                        }]
                }).text)
    print(post('http://localhost:8080/orders',
               json={
                "data": [{
                        "order_id": 16,
                        "weight": 0,
                        "region": 11,
                        "delivery_hours": ["08:00-18:00"]
                        }]
                }).text)
    print(post('http://localhost:8080/orders',
               json={
                "data": [{
                        "order_id": 16,
                        "weight": 17,
                        "region": [],
                        "delivery_hours": ["08:00-18:00"]
                        }]
                }).text)
    print(post('http://localhost:8080/orders',
               json={
                "data": [{
                        "order_id": 16,
                        "weight": 17,
                        "region": [],
                        }]
                }).text)
    print(post('http://localhost:8080/orders',
               json={
                "data": [{
                        "order_id": 16,
                        "weight": 17,
                        "region": [],
                        "delivery_hours": []
                        }]
                }).text)


post_orders()

print('----------------------------------------------------------')

# Проверка валидации данных assign запроса
print('----------------------------------------------------------')


def post_assign():
    print(post('http://localhost:8080/orders/assign',
               json={
                        "courier_id": 5,
                    }).text)
    print(post('http://localhost:8080/orders/assign',
               json={
                        "courier_id": ''
                    }).text)
    print(post('http://localhost:8080/orders/assign',
               json={
                        "courier_id": 8
                    }).text)
    print(post('http://localhost:8080/orders/assign',
               json={

                    }).text)


post_assign()

print('----------------------------------------------------------')

# Проверка валидации данных complete запроса
print('----------------------------------------------------------')


def post_complete():
    print(post('http://localhost:8080/orders/complete',
               json={
                        "courier_id": 5,
                        "order_id": 2,
                        "complete_time": datetime.datetime.now().isoformat()[:-4] + 'Z'
                    }).text)
    print(post('http://localhost:8080/orders/complete',
               json={
                        "order_id": 16,
                        "complete_time": datetime.datetime.now().isoformat()[:-4] + 'Z'
                    }).text)
    print(post('http://localhost:8080/orders/complete',
               json={
                        "courier_id": '',
                        "order_id": 16,
                        "complete_time": datetime.datetime.now().isoformat()[:-4] + 'Z'
                    }).text)
    print(post('http://localhost:8080/orders/complete',
               json={
                        "courier_id": 6,
                        "order_id": '',
                        "complete_time": datetime.datetime.now().isoformat()[:-4] + 'Z'
                    }).text)
    print(post('http://localhost:8080/orders/complete',
               json={
                        "courier_id": 6,
                        "order_id": 16,
                        "complete_time": datetime.datetime.now().isoformat()[:-4]
                    }).text)


post_complete()


print('----------------------------------------------------------')

# Проверка валидации данных get запроса курьера
print('----------------------------------------------------------')


def get_courier():
    print(get('http://localhost:8080/couriers/5').text)
    print(get('http://localhost:8080/couriers/4').text)
    print(get('http://localhost:8080/couriers/7').text)


get_courier()


print('----------------------------------------------------------')

# Проверка валидации данных get запроса заказа
print('----------------------------------------------------------')


def get_orders():
    print(get('http://localhost:8080/orders/5').text)
    print(get('http://localhost:8080/orders/18').text)
    print(get('http://localhost:8080/orders/1').text)


get_orders()


print('----------------------------------------------------------')
