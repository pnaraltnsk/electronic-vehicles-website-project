import datetime, os, random
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import datastore
from flask import Flask, render_template, request, redirect  # framework

app = Flask(__name__)  # flask app object
# __name__ part takes the name of curr file
# and passes it as part of the Flask constructor.
credential_path = "C:/Users/pnral/AppData/Local/Google/Cloud SDK/Cloud Examples/examples-342715-be5d9216fda2.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
datastore_client = datastore.Client()

firebase_request_adapter = requests.Request()


def store_time(email):
    entity = datastore.Entity(key=datastore_client.key('User', email, 'visit'))
    entity.update({'email': email})
    datastore_client.put(entity)


def retrieveUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity


def createUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore.Entity(key=entity_key)
    entity.update({
        'email': claims['email'],
        'name': claims['name'],
        'car_list': []
    })
    datastore_client.put(entity)


def retrieveCar(user_info):
    car_ids = user_info['car_list']
    car_keys = []
    for i in range(len(car_ids)):
        car_keys.append(datastore_client.key('car', car_ids[i]))
    car_list = datastore_client.get_multi(car_keys)
    return car_list


def createEV(claims, obj_name, manufacturer, year, battery_size, wltp_range, cost, power):
    id = random.getrandbits(63)
    entity_key = datastore_client.key('car', id)
    entity = datastore.Entity(key=entity_key)
    entity.update({
        'email': claims['email'],
        'obj_name': obj_name,
        'manufacturer': manufacturer,
        'year': year,
        'battery_size': battery_size,
        'WLTP_range': wltp_range,
        'cost': cost,
        'power': power
    })
    datastore_client.put(entity)
    return id


def addCarToUser(user_info, id):
    car_keys = user_info['car_list']
    car_keys.append(id)
    user_info.update({
        'car_list': car_keys
    })
    datastore_client.put(user_info)


def retrieve_all_entities():
    query = datastore_client.query(kind='car')
    all_keys = list(query.fetch())
    return all_keys


def deleteCar(claims, id):
    user_info = retrieveUserInfo(claims)
    entity_key = datastore_client.key('car', id)
    entity = datastore_client.get(key=entity_key)
    if user_info['email'] == entity['email']:
        datastore_client.delete(entity_key)
        car_ids = user_info['car_list']
        car_ids.remove(id)
        user_info.update({
            'car_list': car_ids
        })
        datastore_client.put(user_info)
    else:
        return False


def updateCarInfo(claims, id, obj_name, manufacturer, year, battery_size, wltp_range, cost, power):
    entity_key = datastore_client.key('car', id)
    entity = datastore_client.get(entity_key)
    if claims['email'] == entity['email']:
        entity.update({
            'email': claims['email'],
            'obj_name': obj_name,
            'manufacturer': manufacturer,
            'year': year,
            'battery_size': battery_size,
            'WLTP_range': wltp_range,
            'cost': cost,
            'power': power
        })
        datastore_client.put(entity)


# these functions below will be for rendering templates
@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    cars = None
    # all_ev = retrieve_all_entities()
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            if user_info is None:
                createUserInfo(claims)
                user_info = retrieveUserInfo(claims)
            cars = retrieveCar(user_info)

        except ValueError as exc:
            error_message = str(exc)

    return render_template('index.html', user_data=claims, error_message=error_message,
                           user_info=user_info, cars=cars)


@app.route('/home')
def home():
    return redirect('/')


@app.route('/list-ev')
def list_cars():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    cars = None
    cars = retrieve_all_entities()
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)

        except ValueError as exc:
            error_message = str(exc)

    return render_template('list.html', user_data=claims, error_message=error_message,
                           cars=cars)


@app.route('/car-info/<int:id>', methods=['POST'])
def detcarinfo_page(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    entity_key = datastore_client.key('car', id)
    result = datastore_client.get(entity_key)
    return render_template('car-info.html', user_data=claims, result=result, id=id)


@app.route('/delete_car/<int:id>', methods=['POST'])
def deleteCarFromUser(id):
    id_token = request.cookies.get("token")
    error_message = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)

            result = deleteCar(claims, id)

        except ValueError as exc:
            error_message = str(exc)
    return redirect('/list')


@app.route('/edit_car_info/<int:id>', methods=['POST'])
def editUserInfo(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            updateCarInfo(claims,id,
                          request.form['obj_name'],
                          request.form['manufacturer'],
                          request.form['year'],
                          request.form['battery_size'],
                          request.form['WLTP_range'],
                          request.form['cost'],
                          request.form['power'])

        except ValueError as exc:
            error_message = str(exc)
    cars = retrieve_all_entities()
    return render_template('list.html', user_data=claims, error_message=error_message,
                           cars=cars)


@app.route('/compare')
def compareEV_page():
    return render_template('compare-ev.html')


@app.route('/add_EV')
def addEV_page():
    return render_template('addEV.html')


@app.route('/add_ev', methods=['POST'])
def addEV():
    id_token = request.cookies.get("token")
    claims = None
    user_info = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            id = createEV(
                claims,
                request.form['obj_name'],
                request.form['manufacturer'],
                request.form['year'],
                request.form['battery_size'],
                request.form['WLTP_range'],
                request.form['cost'],
                request.form['power']
            )
            addCarToUser(user_info, id)

        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/query_multiple_attribs', methods=['POST'])
def queryMultipleAttribs():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    car_info = None
    result = None
    car_info = retrieve_all_entities()

    query = datastore_client.query(kind='car')
    if request.form['obj_name']:
        query.add_filter('obj_name', '=', str(request.form['obj_name']))
    if request.form['manufacturer']:
        query.add_filter('manufacturer', '=', str(request.form['manufacturer']))
    if request.form['year']:
        query.add_filter('ev_list.year', '=', str(request.form['year']))
    if request.form['battery_size']:
        query.add_filter('battery_size', '=', request.form['battery_size'])
    if request.form['WLTP_range']:
        query.add_filter('WLTP_range', '=', request.form['WLTP_range'])
    if request.form['cost']:
        query.add_filter('cost', '=', request.form['cost'])
    if request.form['power']:
        query.add_filter('power', '=', request.form['power'])
    result = list(query.fetch())

    return render_template('list.html', user_data=claims, error_message=error_message,
                           cars=result)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
