import sqlalchemy as db
from jinjasql import JinjaSql


def in_range(table, column, args=None):
    """
    Check whether values in a column fall within a specific range.

    Args:
        - min: the minimum value of the range
        - max: the maximum value of the range
    """
    assert 'min' in args
    assert 'max' in args

    return db.select([table]).where(db.or_(column < args['min'],
                                           column > args['max']))


def unique(table, column, args=None):
    """
    Check whether values in a column are unique.
    """
    return db.select([table]).group_by(column)\
             .having(db.func.count(column) > 1)


def custom_sql(table, column, args=None):
    """
    Execute a custom (optionally Jinja-fromatted) SQL query and fail if
    non-zero number of rows is returned.
    """
    j = JinjaSql(param_style='pyformat')

    if 'query_file' in args:
        q_str = open(args['query_file']).read()
    if 'query' in args:
        q_str = args['query']

    args['table'] = table.name
    args['column'] = column.name

    query, bind_params = j.prepare_query(q_str, args)

    return query % bind_params
