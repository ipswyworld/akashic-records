# publish 1m bars CSV to Kafka topic 'ticks'
import csv, time, json
from kafka import KafkaProducer

KAFKA = 'localhost:29095'
producer = KafkaProducer(bootstrap_servers=[KAFKA],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def publish_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            # expect columns: timestamp, open, high, low, close, volume
            msg = {
                'ts': r['timestamp'],
                'o': float(r['open']),
                'h': float(r['high']),
                'l': float(r['low']),
                'c': float(r['close']),
                'v': float(r.get('volume', 0))
            }
            producer.send('ticks', msg)
            time.sleep(0.01)  # throttle for dev

if __name__ == '__main__':
    publish_csv('data/xauusd_1min.csv')
