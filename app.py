import json
from kafka import KafkaProducer
from flask import Flask, request, jsonify
import os
import time
import pymongo
from database import connection_url, init_db, db_session
from models import MessageModel, HostageSentenceModel, ExplosiveSentenceModel

app = Flask(__name__)

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
mongo_host = os.environ.get('MONGO_HOST', 'localhost')

print(mongo_host)

def connect_mongo():
    while True:
        try:
            # ניסיון חיבור ל-MongoDB
            client = pymongo.MongoClient(
                host=mongo_host,
                port=27017,
                serverSelectionTimeoutMS=5000
            )
            # בדיקת תקינות החיבור
            client.admin.command('ismaster')
            print("Connected to MongoDB", client)

            # גישה למסד הנתונים והאוסף
            db = client['message_monitoring']
            collection = db['all_messages']
            return collection
        except Exception as e:
            # רישום שגיאה עם פרטים ברורים
            print(f"MongoDB connection error: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(20)  # השהייה לפני ניסיון נוסף

coll = connect_mongo()


# connect to mongoDB in docker:
# docker exec -it <container_name_or_id> mongo

# basic mongo commands:
# show databases
# use message_monitoring
# show collections
# db.collectionName.find()
# db.collectionName.count()

app.config["SQLALCHEMY_DATABASE_URI"] = connection_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True


with app.app_context():
    init_db()


# docker exec -it my_postgres psql -U myuser -d mydb



@app.route('/api/email', methods=['POST'])
def receive_email():
    message = request.get_json()
    producer.send('messages.all', value=message)
    res = coll.insert_one(message)
    print(res)
    return jsonify({"message": "message added successfully"}), 201

@app.route('/api/email_suspicious_content', methods=['GET'])
def get_suspicious_content_by_email():
    try:
        email = request.args.get('email')
    except Exception as e:
        return jsonify({"message": 'did not receive email', "error": str(e)}), 400

    hostage_res = (
        db_session.query(HostageSentenceModel)
        .join(MessageModel, HostageSentenceModel.message)  # Explicit join with MessageModel
        .filter(MessageModel.email == email)  # Filter by email
        .all()
    )

    explosive_res = (
        db_session.query(ExplosiveSentenceModel)
        .join(MessageModel, ExplosiveSentenceModel.message)  # Explicit join with MessageModel
        .filter(MessageModel.email == email)  # Filter by email
        .all()
    )
    hostage_content = [message.sentence for message in hostage_res]
    explosive_content = [message.sentence for message in explosive_res]

    print(type(hostage_content))
    print(type(explosive_content))
    return jsonify({"email": email, "emails with 'hostage'": hostage_content, "emails with 'explosive'": explosive_content}), 200


if __name__ == '__main__':
    app.run(port=5000)

# meaganyoung@example.net
# markhunt@example.net
# brendachan@example.org
# rmartinez@example.com