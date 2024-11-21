import json
from kafka import KafkaConsumer
from database import db_session
from models import MessageModel, LocationModel, DeviceInfoModel, ExplosiveSentenceModel

consumer = KafkaConsumer(
    'messages.explosive',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='explosive-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    message_content = message.value[6]
    new_message = MessageModel()
    for key in list(message_content.keys())[:5]:
        if hasattr(new_message, key):
            setattr(new_message, key, message_content[key])
    db_session.add(new_message)

    location = LocationModel()
    for key, value in message_content['location'].items():
        if hasattr(location, key):
            setattr(location, key, value)
    location.message_id = message_content['id']
    db_session.add(location)

    device_info = DeviceInfoModel()
    for key, value in message_content['device_info'].items():
        if hasattr(device_info, key):
            setattr(device_info, key, value)
    device_info.message_id = message_content['id']
    db_session.add(device_info)

    for sen in message_content['sentences']:
        if 'explos' in sen:
            new_sen = ExplosiveSentenceModel(sentence=sen, message_id=message_content['id'])
            db_session.add(new_sen)

    db_session.commit()