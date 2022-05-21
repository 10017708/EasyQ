import queue
import random
import string
from flask import Flask, jsonify, request

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate('serviceAccountKey.json')

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://easyq-af40b-default-rtdb.firebaseio.com'
})

ref = db.reference('hello')

app = Flask(__name__)

@app.route('/get/queue/<string:user_id>/<string:queue_id>')
def get_queue(user_id, queue_id):
    ref = db.reference(queue_id)
    return jsonify(
        {"name": ref.child("name").get(), 
        "position": ref.child("users").child(user_id).get()
        }
    )

@app.route('/delete/queue/<string:user_id>/<string:queue_id>')
def delete_queue(user_id, queue_id):
    if(db.reference("/" + queue_id).child("owner_id").get() == user_id):
        db.reference("/").child(queue_id).delete()
    return jsonify({"success": True})


@app.route('/leave/queue/<string:user_id>/<string:queue_id>')
def leave_queue(user_id, queue_id):
    ref = db.reference(queue_id)
    ref.child("users").child(user_id).delete()
    return jsonify({"success": True})

@app.route('/join/queue/<string:user_id>/<string:queue_id>/<string:name>')
def join_queue(user_id, queue_id, name):
    ref = db.reference(queue_id + "/users")
    pos = db.reference(queue_id).child("lastPosition").get()
    db.reference(queue_id).child("lastPosition").set(pos + 1)
    leave_queue(user_id, queue_id)
    ref.child(user_id).set(
        {
            "name": str(name),
            "position": pos + 1
        }
    )
    return(jsonify({"success": True}))

@app.route("/create/queue/<string:user_id>/<string:name>/")
def create_queue(user_id, name):
    queue_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    
    while(db.reference(queue_id).child("name").get() is not None):
        queue_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

    ref = db.reference(queue_id).set(
        {
            "name": str(name),
            "owner_id": str(user_id),
            "lastPosition": 0
        }
    )

    return({"success": True, "queue_id": queue_id})





if __name__ == '__main__':
    app.run(debug=True)
