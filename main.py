import datetime, os, random
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import datastore
from flask import Flask, render_template, request, redirect #framework

app = Flask(__name__) #flask app object
# __name__ part takes the name of curr file
# and passes it as part of the Flask constructor.
credential_path = "C:/Users/pnral/AppData/Local/Google/Cloud SDK/Cloud Examples/examples-342715-be5d9216fda2.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
datastore_client = datastore.Client()

firebase_request_adapter = requests.Request()


def store_time(email, dt):
    entity = datastore.Entity(key = datastore_client.key('User', email,'visit'))
    entity.update({'timestamp' : dt})
    datastore_client.put(entity)

def fetch_times(email, limit):
    ancestor_key = datastore_client.key('User', email)

    query = datastore_client.query(kind='visit', ancestor=ancestor_key)
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)
    return times

def retrieveUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity

def createUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'email': claims['email'],
        'name': claims['name'],
        'ev_list': []
    })
    datastore_client.put(entity)

def retrieveEVs(user_info):
    ev_ids = user_info['ev_list']
    ev_keys = []
    for i in range(len(ev_ids)):
        ev_keys.append(datastore_client.key('EV', ev_ids[i]))
    ev_list = datastore_client.get_multi(ev_keys)
    return ev_list

def createEV(obj_name, manufacturer, year, battery_size, wltp_range, cost, power):
    entity = datastore.Entity()
    entity.update({
        'obj_name': obj_name,
        'manufacturer': manufacturer,
        'year': year,
        'battery_size': battery_size,
        'WLTP_range': wltp_range,
        'cost': cost,
        'power': power
    })
    return entity

def addEVToUser(user_info, ev_entity):
    evs = user_info['ev_list']
    evs.append(ev_entity)
    user_info.update({
        'ev_list': evs
    })
    datastore_client.put(user_info)

def deleteEV(claims, id):
    user_info = retrieveUserInfo(claims)
    ev_list = user_info['ev_list']

    del ev_list[id]
    user_info.update({
        'ev_list' : ev_list
    })
    datastore_client.put(user_info)

def retrieve_all_entities():
    query = datastore_client.query(kind='UserInfo')
    all_keys = query.fetch()
    return all_keys

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
            ev = createEV(request.form['obj_name'],
            request.form['manufacturer'], request.form['year'], request.form['battery_size']
            , request.form['WLTP_range'], request.form['cost'], request.form['power'])
            addEVToUser(user_info, ev)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')

@app.route('/delete_ev/<int:id>', methods=['POST'])
def deleteEVFromUser(id):
    id_token = request.cookies.get("token")
    error_message = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
        firebase_request_adapter)
            deleteEV(claims, id)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')




@app.route('/')

def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    electric_v = None

    all_ev = retrieve_all_entities()
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
    firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            if user_info == None:
                createUserInfo(claims)
                user_info = retrieveUserInfo(claims)
        except ValueError as exc:
            error_message = str(exc)


    return render_template('index.html', user_data=claims, error_message=error_message,
    user_info=user_info, all_ev=all_ev)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
