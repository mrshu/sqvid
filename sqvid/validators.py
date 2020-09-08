import sqlalchemy as db
from jinjasql import JinjaSql


def in_range(table, column, args=None):
    """
    Check whether values in a column fall within a specific range.

    Args:
        min (int): the minimum value of the range
        max (int): the maximum value of the range

    Example:
      .. code:: toml

        [[test_sqvid_db.suppliers.SupplierID]]
        validator = 'in_range'
        args = {min = 1, max = 256}

    """
    assert 'min' in args
    assert 'max' in args

    return db.select([table]).where(db.or_(column < args['min'],
                                           column > args['max']))


def accepted_values(table, column, args=None):
    """
    Check that a column contains only specified values.

    Args:
        vals (list): a list of values

    Example:
      .. code:: toml

        [[test_sqvid_db.suppliers.Country]]
        validator = 'accepted_values'
        args.vals  = [
          'USA',
          'UK',
          'Spain',
          'Japan',
          'Germany',
          'Australia',
          'Sweden',
          'Finland',
          'Italy',
          'Brazil',
          'Singapore',
          'Norway',
          'Canada',
          'France',
          'Denmark',
          'Netherlands'
        ]


    """
    assert 'vals' in args

    return db.select([table]).where(column.notin_(args['vals']))


def not_null(table, column, args=None):
    """
    Check that a column contains only non-`NULL` values.

    Example:
      .. code:: toml

        [[test_sqvid_db.suppliers.SupplierID]]
        validator = 'not_null'
    """
    return db.select([table]).where(column.is_(None))


def unique(table, column, args=None):
    """
    Check whether values in a column are unique.

    Example:
      .. code:: toml

        [[test_sqvid_db.suppliers.SupplierID]]
        validator = 'unique'
    """
    return db.select([column]) \
        .select_from(table) \
        .group_by(column) \
        .having(db.func.count(column) > 1)


def custom_sql(table, column, args=None):
    """
    Execute a custom (optionally Jinja-formatted) SQL query and fail if
    non-zero number of rows is returned.

    Either ``query`` or ``query_file`` parameter needs to be provided. All the
    other arguments are passed as Jinja variables and can be used to build the
    query.

    Args:
        query (str): query to be executed (optional).
        query_file (str): path to the file in which the query to be executed
                          can be found (optional)

    Example:
      .. code:: toml

        [[test_sqvid_db.suppliers.SupplierID]]
        validator = 'custom_sql'
        args.query_file = './tests/queries/tables_equal_rows.sql'
        args.other_table = 'suppliers_copy'
    """
    j = JinjaSql(param_style='pyformat')

    if 'query_file' in args:
        q_str = open(args['query_file']).read()
    if 'query' in args:
        q_str = args['query']

    args['table'] = table.name
    args['column'] = column.name

    query, bind_params = j.prepare_query(q_str, args)

    binded_query = query % bind_params

    # Ensure custom_sql query does not end with a semicolon, so that things
    # like LIMIT can be appended to it.
    q = binded_query.strip()
    if q.endswith(';'):
        context = q[10:]
        raise ValueError(f'Custom SQL query for [{table.name}.{column.name}]'
                         f" cannot end with a semicolon: ...'{context}'")

    return binded_query
