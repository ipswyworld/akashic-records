# simple consumer that subscribes to 'ticks' and writes bars to TimescaleDB (table: bars)
import json, time
from kafka import KafkaConsumer
import pandas as pd
from sqlalchemy import create_engine, text

KAFKA = 'localhost:29095'
consumer = KafkaConsumer('ticks', bootstrap_servers=[KAFKA], value_deserializer=lambda m: json.loads(m.decode('utf-8')))
engine = create_engine('postgresql://trader:example@localhost:5435/golddb')

# create table if not exists
with engine.connect() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS bars (
      ts TIMESTAMP PRIMARY KEY,
      open DOUBLE PRECISION,
      high DOUBLE PRECISION,
      low DOUBLE PRECISION,
      close DOUBLE PRECISION,
      volume DOUBLE PRECISION
    );
    SELECT create_hypertable('bars', 'ts', if_not_exists => TRUE);
    """))

for msg in consumer:
    m = msg.value
    df = pd.DataFrame([{
        'ts': pd.to_datetime(m['ts']),
        'open': m['o'], 'high': m['h'], 'low': m['l'], 'close': m['c'], 'volume': m['v']
    }])
    df.to_sql('bars', engine, if_exists='append', index=False, method='multi')
