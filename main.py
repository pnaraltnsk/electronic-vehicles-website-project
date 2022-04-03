import datetime, os, random
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import datastore
from flask import Flask, render_template, request, redirect, url_for  # framework

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
        'power': power,
        'review_list': [],
        'rating_list': []
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
    datastore_client.delete(entity_key)
    car_ids = user_info['car_list']
    car_ids.remove(id)
    user_info.update({
        'car_list': car_ids
    })
    datastore_client.put(user_info)


def updateCarInfo(claims, id, obj_name, manufacturer, year, battery_size, wltp_range, cost, power):
    entity_key = datastore_client.key('car', id)
    entity = datastore_client.get(entity_key)

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


@app.route('/car-info<int:id>')
def detcarinfo_page(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    avg_rate = 0
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    entity_key = datastore_client.key('car', id)
    result = datastore_client.get(entity_key)
    for rate in result['rating_list']:
        avg_rate += int(rate)
    return render_template('car-info.html', user_data=claims, result=result, avg_rate=avg_rate, id=id)


@app.route('/delete_car/<int:id>', methods=['POST'])
def deleteCarFromUser(id):
    id_token = request.cookies.get("token")
    error_message = None
    cars = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)

            deleteCar(claims, id)
            cars = retrieve_all_entities()
        except ValueError as exc:
            error_message = str(exc)
    return render_template('list.html', user_data=claims, error_message=error_message,
                           cars=cars)


@app.route('/add_review/<int:id>', methods=['POST'])
def addReview(id):
    id_token = request.cookies.get("token")
    error_message = None
    cars = None
    claims = None
    result = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)

        except ValueError as exc:
            error_message = str(exc)
        entity_key = datastore_client.key('car', id)
        entity = datastore_client.get(entity_key)
        reviews = entity['review_list']
        ratings = entity['rating_list']
        print(request.form.get('rating'))
        reviews.append(request.form.get('revieww'))
        ratings.append(request.form.get('rating'))
        entity.update({
            'review_list': reviews,
            'rating_list': ratings
        })
        datastore_client.put(entity)
        result = datastore_client.get(entity_key)
    # return render_template('car-info.html', user_data=claims, result=result, id=id)
    return redirect(url_for('detcarinfo_page', id=id))


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
            updateCarInfo(claims, id,
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

    return render_template('compare-ev.html', user_data=claims, error_message=error_message,
                           cars=cars, chck=True)


@app.route('/compare_cars', methods=['POST'])
def compare_cars():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    cars = None
    cars = retrieve_all_entities()
    compare = None
    car_list = []
    minValue = [0] * 5
    maxValue = [0] * 5
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)

        except ValueError as exc:
            error_message = str(exc)

    chckbx = request.form.getlist('checkboxes')
    if len(chckbx) <= 1:
        return render_template('compare-ev.html', user_data=claims, error_message=error_message,
                               cars=cars, chck=False)

    for id in chckbx:
        car_list.append(datastore_client.key('car', int(id)))

    compare = datastore_client.get_multi(car_list)

    for i in range(len(compare)):
        comp = compare[i]
        for j in range(0, len(compare)):
            comp2 = compare[j]
            if comp['year'] <= comp2['year']:
                if minValue[0] == 0 or int(minValue[0]) > int(comp['year']):
                    minValue[0] = comp['year']
            else:
                if int(maxValue[0]) < int(comp['year']):
                    maxValue[0] = comp['year']

            if comp['battery_size'] <= comp2['battery_size']:
                if minValue[1] == 0 or int(minValue[1]) > int(comp['battery_size']):
                    minValue[1] = comp['battery_size']
            else:
                if int(maxValue[1]) < int(comp['battery_size']):
                    maxValue[1] = comp['battery_size']

            if comp['WLTP_range'] <= comp2['WLTP_range']:
                if minValue[2] == 0 or int(minValue[2]) > int(comp['WLTP_range']):
                    minValue[2] = comp['WLTP_range']
            else:
                if int(maxValue[2]) < int(comp['WLTP_range']):
                    maxValue[2] = comp['WLTP_range']

            if comp['cost'] <= comp2['cost']:
                if minValue[3] == 0 or int(minValue[3]) > int(comp['cost']):
                    minValue[3] = comp['cost']
            else:
                if int(maxValue[3]) < int(comp['cost']):
                    maxValue[3] = comp['cost']

            if comp['power'] <= comp2['power']:
                if minValue[4] == 0 or int(minValue[4]) > int(comp['power']):
                    minValue[4] = comp['power']
            else:
                if int(maxValue[4]) < int(comp['power']):
                    maxValue[4] = comp['power']

        print(comp['power'])
    print(minValue)
    print(maxValue)
    return render_template('compare.html', user_data=claims, error_message=error_message,
                           cars=cars, compare=compare, minVal=minValue, maxVal=maxValue)


@app.route('/add_EV')
def addEV_page():
    return render_template('addEV.html', add=True)


@app.route('/add_ev', methods=['POST'])
def addEV():
    id_token = request.cookies.get("token")
    claims = None
    cars = None
    error_message = None
    user_info = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            cars = retrieve_all_entities()
            for car in cars:
                if car['obj_name'] == request.form['obj_name'] and car['manufacturer'] == request.form['manufacturer'] \
                        and car['year'] == request.form['year']:
                    return render_template('addEV.html', add=False)

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
            cars = retrieve_all_entities()
        except ValueError as exc:
            error_message = str(exc)
    return render_template('list.html', user_data=claims, error_message=error_message,
                           cars=cars)


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
        query.add_filter('year', '=', request.form['year'])
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
