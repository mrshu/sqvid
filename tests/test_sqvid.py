from sqvid import __version__
import sqlalchemy as db
import sqvid
import pytest
import sqlite3
import os
from click.testing import CliRunner
DIRNAME = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def engine():
    db_path = DIRNAME + '/test_sqvid_db.sqlite'
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Import the DB from https://github.com/AndrejPHP/w3schools-database
    with open(DIRNAME + '/test_db.sql') as f:
        cur.executescript(f.read())
    conn.close()

    return db.create_engine('sqlite:///' + DIRNAME + '/test_sqvid_db.sqlite')


def test_version():
    assert __version__ == '0.1.0'


def test_raw_in_range_validation(engine):
    conn = engine.connect()
    t = sqvid.executor.prepare_table(engine, 'suppliers')
    s = sqvid.validators.in_range(t, t.columns['SupplierID'],
                                  args={
                                      'min': 1,
                                      'max': 30
                                  })
    ll = conn.execute(s).fetchall()
    assert len(ll) == 0


def test_execute_in_range_validation(engine):
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'SupplierID',
                                                sqvid.validators.in_range,
                                                args={
                                                    'min': 1,
                                                    'max': 30
                                                })
    assert len(r) == 0


def test_execute_in_range_validation_with_fail(engine):
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'SupplierID',
                                                sqvid.validators.in_range,
                                                args={
                                                    'min': 3,
                                                    'max': 30
                                                })
    assert len(r) == 2

    o = [(1, 'Exotic Liquid', 'Charlotte Cooper',
          '49 Gilbert St.', 'Londona', 'EC1 4SD', 'UK', '(171) 555-2222'),
         (2, 'New Orleans Cajun Delights', 'Shelley Burke',
          'P.O. Box 78934', 'New Orleans', '70117', 'USA', '(100) 555-4822')]

    assert r == o


def test_execute_in_range_validation_custom_column(engine):
    c = 'SupplierID - 5'
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'SupplierID',
                                                sqvid.validators.in_range,
                                                args={
                                                    'min': 1,
                                                    'max': 30
                                                },
                                                custom_column=c)
    assert len(r) == 5


def test_execute_in_range_validation_custom_column_with_fail(engine):
    c = 'SupplierID * 5'
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'SupplierID',
                                                sqvid.validators.in_range,
                                                args={
                                                    'min': 1,
                                                    'max': 30
                                                },
                                                custom_column=c)
    assert len(r) == 23


def test_execute_not_null_validation(engine):
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'products',
                                                'ProductID',
                                                sqvid.validators.not_null)
    assert len(r) == 0


def test_execute_not_null_validation_with_fail(engine):
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'products',
                                                'Price',
                                                sqvid.validators.not_null)
    assert len(r) == 1
    assert r == [(78, 'Chocolade', 22, 3, '100 pkgs.', None)]


def test_execute_unique_validation(engine):
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'SupplierID',
                                                sqvid.validators.unique)
    assert len(r) == 0


def test_execute_accepted_values_validation(engine):
    accepted_values = [
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
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'Country',
                                                sqvid.validators.accepted_values, # noqa
                                                args={
                                                    'vals': accepted_values
                                                })

    assert len(r) == 0


def test_execute_accepted_values_validation_fail(engine):
    accepted_values = [
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
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers_missing_first_3_append_last_3', # noqa
                                                'Country',
                                                sqvid.validators.accepted_values, # noqa
                                                args={
                                                    'vals': accepted_values
                                                })

    assert len(r) == 3
    assert r == [
        (30, 'Escargots Nouveaux', 'Marie Delamare', '22, rue H. Voiron',
         'Montceau', '71300', 'Malawi', '85.57.00.07'),
        (31, 'Gai pâturage', 'Eliane Noz', 'Bat. B 3, rue des Alpes',
         'Annecy', '74000', 'Argentina', '38.76.98.06'),
        (32, "Forêts d'érables", 'Chantal Goulet', '148 rue Chasseur',
         'Ste-Hyacinthe', 'J2S 7S8', 'Peru', '(514) 555-2955')
    ]


def test_execute_unique_validation_with_fail(engine):
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'orders',
                                                'CustomerID',
                                                sqvid.validators.unique)
    assert len(r) == 52


def test_execute_custom_sql_query_validation(engine):
    args = {
        'query': 'SELECT * FROM {{ table }} WHERE {{ column }} > {{ val }}',
        'val': 50
    }
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'SupplierID',
                                                sqvid.validators.custom_sql,
                                                args=args)
    assert len(r) == 0


def test_execute_custom_sql_query_validation_fail(engine):
    args = {
        'query': 'SELECT * FROM {{ table }} WHERE {{ column }} > {{ val }}',
        'val': 25
    }
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'SupplierID',
                                                sqvid.validators.custom_sql,
                                                args=args)
    assert len(r) == 4


def test_execute_custom_sql_file_validation_fail(engine):
    args = {
        'query_file': './tests/queries/tables_equal_rows.sql',
        'other_table': 'suppliers_missing_first_3'
    }
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'SupplierID',
                                                sqvid.validators.custom_sql,
                                                args=args)
    assert len(r) == 3


def test_execute_custom_sql_file_validation_fail_again(engine):
    args = {
        'query_file': './tests/queries/tables_equal_rows.sql',
        'other_table': 'suppliers_missing_first_3_append_last_3'
    }
    r, _, _ = sqvid.executor.execute_validation(engine,
                                                'suppliers',
                                                'SupplierID',
                                                sqvid.validators.custom_sql,
                                                args=args)
    assert len(r) == 6


def test_e2e_run():
    runner = CliRunner()
    config_files = [
        './tests/configs/test.toml',
        './tests/configs/extended_test.toml'
    ]

    for c in config_files:
        result = runner.invoke(sqvid.console.run,
                               ['--config', c])
        assert result.exit_code == 0

        # Same thing with verbose
        result = runner.invoke(sqvid.console.run,
                               ['--config', c, '--verbose'])
        assert result.exit_code == 0


def test_e2e_run_with_fail():
    runner = CliRunner()
    config_files = [
        './tests/configs/test_fail.toml',
        './tests/configs/extended_test_fail.toml'
    ]

    for c in config_files:
        result = runner.invoke(sqvid.console.run,
                               ['--config', c])
        assert result.exit_code == 1

        # Same thing with verbose
        result = runner.invoke(sqvid.console.run,
                               ['--config', c, '--verbose'])
        assert result.exit_code == 1
