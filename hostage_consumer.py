import json

from kafka import KafkaConsumer

from database import db_session
from models import MessageModel, LocationModel, DeviceInfoModel, HostageSentenceModel

consumer = KafkaConsumer(
    'messages.hostage',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='hostage-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    message_content = message.value[6]
    new_message = MessageModel()
    for key in list(message_content.keys())[:5]:
        if hasattr(new_message, key):  # Ensure the key is a valid attribute
            setattr(new_message, key, message_content[key])
    db_session.add(new_message)
    db_session.commit()

    location = LocationModel()
    for key, value in message_content['location'].items():
        if hasattr(location, key): setattr(location, key, value)
    location.message_id = message_content['id']
    db_session.add(location)
    db_session.commit()

    device_info = DeviceInfoModel()
    for key, value in message_content['device_info'].items():
        if hasattr(device_info, key): setattr(device_info, key, value)
    device_info.message_id = message_content['id']
    db_session.add(device_info)
    db_session.commit()

    for sen in message_content.get('sentences', []):
        if 'hostage' in sen:

            new_sen = HostageSentenceModel(sentence=sen, message_id=message_content['id'])
            db_session.add(new_sen)
            db_session.commit()

