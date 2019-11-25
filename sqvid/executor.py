import sqlalchemy as db
from importlib import import_module
import envtoml


def prepare_table(engine, table_name):
    metadata = db.MetaData()
    return db.Table(table_name, metadata, autoload=True, autoload_with=engine)


def execute_validation(engine, table, column, validator, args=None,
                       custom_column=None):
    conn = engine.connect()
    t = prepare_table(engine, table)
    col = t.columns[column]

    # If a custom column has been specified, use it in place of the column from
    # the table
    if custom_column:
        col = db.sql.literal_column(custom_column)

    s = validator(t, col, args=args)
    ex = conn.execute(s)

    if type(s) == str:
        bare_query = s
    else:
        compile_kwargs = {"literal_binds": True}
        bare_query = s.compile(engine, compile_kwargs=compile_kwargs)

    return ex.fetchall(), ex.keys(), bare_query


def execute_validations(config):
    cfg = envtoml.load(config)

    engine = db.create_engine(cfg['general']['sqla'])
    db_name = cfg['general']['db_name']

    validator_module = import_module('.validators', package='sqvid')

    for table in cfg[db_name]:
        for column in cfg[db_name][table]:
            for val in cfg[db_name][table][column]:
                validator_name = val['validator']
                args = val.get('args')
                custom_column = val.get('custom_column')
                severity = val.get('severity', 'error')

                validator_fn = getattr(validator_module, validator_name)
                r, k, q = execute_validation(engine, table, column,
                                             validator_fn, args,
                                             custom_column=custom_column)

                col_names = val.get('report_columns', k)

                col_name = column
                if custom_column:
                    col_name = "{} (customized as '{}')".format(column,
                                                                custom_column)

                out = ''
                result = 'passed'
                if len(r) == 0:
                    result = 'passed'
                    out = "{}: Validation on [{}] {}.{} of {}{}".format(
                        result.upper(),
                        db_name,
                        table,
                        col_name,
                        validator_name,
                        '({})'.format(args) if args else ''
                    )
                else:
                    if severity == 'warn':
                        result = 'failed (warn only)'
                    else:
                        result = 'failed'

                    out = "{}: Validation on [{}] {}.{} of {}{}".format(
                        result.upper(),
                        db_name,
                        table,
                        col_name,
                        validator_name,
                        '({})'.format(args) if args else '',
                    )

                yield {
                    'query': q,
                    'result': result,
                    'output': out,
                    'rows': list(map(dict, r)),
                    'col_names': col_names
                }
