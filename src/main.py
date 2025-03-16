from sqlite3 import register_adapter

import psycopg2
from peewee import *
from fastapi import FastAPI
import datetime

app = FastAPI()

db_key = open("../db.spreng")
db_items = ["","","",""]
for i in range(4):
    db_items[i] = db_key.readline()
db_key.close()

db = PostgresqlDatabase(db_items[0].strip(),
                        user=db_items[1].strip(),
                        password=db_items[2].strip(),
                        host=db_items[3].strip())

class Package(Model):
    class Meta:
        database = db
        schema = 'sprengendbox'
        table_name = 'packages'

    id = AutoField()  # Serial primary key
    package_name = CharField(max_length=48)
    package_description = CharField(max_length=512)
    package_version = CharField(max_length=16)
    package_download_link = CharField(max_length=512)
    last_update = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')],
        default=datetime.datetime.now()
    )

db.connect()
db.create_tables([Package], safe=True)

@app.get("/")
def read_root():
    return {"message": "please check https://endstone.dev/"}

@app.get("/search/{search_term:path}")
async def search(search_term: str):
    if search_term != "":
        query = (Package
                 .select()
                 .where(Package.package_name.contains(search_term)))
        return list(query.dicts())
    else:
        return {}

@app.get("/fetch_latest/{amount:path}")
async def fetch_latest(amount: int):
    query = (Package.select()
              .order_by(Package.last_update.desc())
              .limit(amount))
    return list(query.dicts())