import sqlalchemy as db


def prepare_table(engine, table_name):
    metadata = db.MetaData()
    return db.Table(table_name, metadata, autoload=True, autoload_with=engine)


def execute_validation(engine, table, column, validator, args=None):
    conn = engine.connect()
    t = prepare_table(engine, table)
    s = validator(t, t.columns[column], args=args)
    ex = conn.execute(s)
    return ex.fetchall(), ex.keys()
