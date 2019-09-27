import sqlalchemy as db


def prepare_table(engine, table_name):
    metadata = db.MetaData()
    return db.Table(table_name, metadata, autoload=True, autoload_with=engine)


def execute_validation(engine, table, column, validator, args=None):
    conn = engine.connect()
    t = prepare_table(engine, table)
    s = validator(t, t.columns[column], args=args)
    ex = conn.execute(s)

    if type(s) == str:
        bare_query = s
    else:
        compile_kwargs = {"literal_binds": True}
        bare_query = s.compile(engine, compile_kwargs=compile_kwargs)

    return ex.fetchall(), ex.keys(), bare_query
