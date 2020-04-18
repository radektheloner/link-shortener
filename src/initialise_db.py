'''
Copyright (C) 2020 Link Shortener Authors (see AUTHORS in Documentation).
Licensed under the MIT (Expat) License (see LICENSE in Documentation).
'''
import uuid

from sanic import Blueprint

from aiomysql.sa import create_engine

from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy.schema import CreateTable


initdb_blueprint = Blueprint('intitialise_db')

metadata = MetaData()
initdb_blueprint.active_table = Table(
    'active_links',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('identifier', String(36)),
    Column('owner', String(50)),
    Column('owner_id', String(255)),
    Column('endpoint', String(20), unique=True),
    Column('url', String(300))
)
initdb_blueprint.inactive_table = Table(
    'inactive_links',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('identifier', String(36)),
    Column('owner', String(50)),
    Column('owner_id', String(255)),
    Column('endpoint', String(20)),
    Column('url', String(300))
)
active_data = [
    (
        str(uuid.uuid1())[:36],
        'vojtech.janousek@applifting.cz',
        '100793120005790639839',
        'pomuzemesi',
        'https://staging.pomuzeme.si'
    ),
    (
        str(uuid.uuid1())[:36],
        'vojtech.janousek@applifting.cz',
        '100793120005790639839',
        'vlk',
        'http://www.vlk.cz'
    ),
    (
        str(uuid.uuid1())[:36],
        'vojtech.janousek@applifting.cz',
        '100793120005790639839',
        'manatee',
        'https://cdn.mos.cms.futurecdn.net/sBVkBoQfStZJWtLwgFRtPi-320-80.jpg'
    ),
    (
        str(uuid.uuid1())[:36],
        'radek.holy@applifting.cz',
        'unknown',
        'dollar',
        'https://i.kym-cdn.com/entries/icons/facebook/000/013/285/gangsta-animals.jpg'
    ),
    (
        str(uuid.uuid1())[:36],
        'radek.holy@applifting.cz',
        'unknown',
        'kodex',
        'https://github.com/Applifting/culture'
    ),
    (
        str(uuid.uuid1())[:36],
        'radek.holy@applifting.cz',
        'unknown',
        'meta',
        'https://github.com/Applifting/link-shortener'
    )
]
inactive_data = [
    (
        str(uuid.uuid1())[:36],
        'vojtech.janousek@applifting.cz',
        '100793120005790639839',
        'tunak',
        'https://www.britannica.com/animal/tuna-fish'
    ),
    (
        str(uuid.uuid1())[:36],
        'radek.holy@applifting.cz',
        'unknown',
        'nope',
        'https://www.youtube.com/watch?v=gvdf5n-zI14'
    )
]


@initdb_blueprint.listener('before_server_start')
async def initialise_db(app, loop):
    app.engine = await create_engine(
        host='db',
        port=3306,
        user='user',
        password='password',
        db='db',
        loop=loop
    )
    async with app.engine.acquire() as conn:
        try:
            trans = await conn.begin()
            await conn.execute(
                str(CreateTable(
                        initdb_blueprint.active_table).compile(app.engine)
                    )
            )
            await conn.execute(
                str(CreateTable(
                        initdb_blueprint.inactive_table).compile(app.engine)
                    )
            )
            for values in active_data:
                await conn.execute(
                    'INSERT INTO active_links \
                     (identifier, owner, owner_id, endpoint, url) \
                     VALUES (%s, %s, %s, %s, %s)',
                    values
                )
            for values in inactive_data:
                await conn.execute(
                    'INSERT INTO inactive_links \
                     (identifier, owner, owner_id, endpoint, url) \
                     VALUES (%s, %s, %s, %s, %s)',
                    values
                )
            await trans.commit()
            await trans.close()

        except Exception as error:
            print(str(error) + '\n' + 'Table are already cached')


@initdb_blueprint.listener('after_server_stop')
async def close_engine(app, loop):
    app.engine.terminate()
    await app.engine.wait_closed()
