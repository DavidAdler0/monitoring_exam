import json

from kafka import KafkaConsumer, KafkaProducer

consumer = KafkaConsumer(
    'messages.all',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)
producer2 = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

for message in consumer:
    print(message)
    fixed_sentences = []
    for sentence in message.value['sentences']:
        if 'hostage' in sentence or 'explos' in sentence:
            fixed_sentences.append(sentence)
    for sentence in message.value['sentences']:
        if sentence not in fixed_sentences:
            fixed_sentences.append(sentence)
    message.value['sentences'] = fixed_sentences
    print(message.value['sentences'])
    for sentence in message.value['sentences']:
        if 'hostage' in sentence:
            producer2.send('messages.hostage', value=message)
        if 'explos' in sentence:
            producer2.send('messages.explosive', value=message)

