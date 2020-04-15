'''
Copyright (C) 2020 Link Shortener Authors
Licensed under the MIT (Expat) License. See the LICENSE file found in the
top-level directory of this distribution.
'''
from sanic import Blueprint

from aiomysql import create_pool
from aiomysql.sa import create_engine

from sqlalchemy import MetaData, Table, Column, String, Integer, Sequence
from sqlalchemy.schema import CreateTable


initdb_blueprint = Blueprint('intitialise_db')

metadata = MetaData()
initdb_blueprint.table = Table(
    'links',
    metadata,
    Column('owner', String(50)),
    Column('endpoint', String(20), unique=True),
    Column('url', String(300))
)
initial_data = [
    (
        'vojtech.janousek@applifting.cz',
        'pomuzemesi',
        'https://staging.pomuzeme.si'
    ),
    (
        'vojtech.janousek@applifting.cz',
        'vlk',
        'http://www.vlk.cz'
    ),
    (
        'radek.holy@applifting.cz',
        'kodex',
        'https://github.com/Applifting/culture'
    ),
    (
        'radek.holy@applifting.cz',
        'meta',
        'https://github.com/Applifting/link-shortener'
    )
]

@initdb_blueprint.listener('before_server_start')
async def initialise_db(app, loop):
    pool = await create_pool(
        host='db',
        port=3306,
        user='user',
        password='password',
        db='db',
        loop=loop,
        autocommit=True
    )
    app.engine = await create_engine(
        host='db',
        port=3306,
        user='user',
        password='password',
        db='db',
        loop=loop
    )
    async with pool.acquire() as conn:
        db_cursor = await conn.cursor()
        try:
            await db_cursor.execute(str(CreateTable(initdb_blueprint.table)))
            await db_cursor.executemany(
                'INSERT INTO links (owner, endpoint, url) VALUES (%s, %s, %s)',
                initial_data
            )

        except Exception as error:
            print(str(error) + '\n' + 'Table is probably already cached')

        await db_cursor.close()

    pool.terminate()
    await pool.wait_closed()


@initdb_blueprint.listener('after_server_stop')
async def close_engine(app, loop):
    app.engine.terminate()
    await app.engine.wait_closed()
