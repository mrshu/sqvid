from envtoml import load
import sqlalchemy as db
from importlib import import_module
from .executor import execute_validation
from nicetable.nicetable import NiceTable
import sys
import click


@click.command()
@click.option('--config',
              type=click.Path(exists=True),
              required=True,
              help='Path to a .toml config file.')
def run(config):
    """Validator of data that is queriable via SQL."""
    cfg = load(config)

    engine = db.create_engine(cfg['general']['sqla'])
    db_name = cfg['general']['db_name']

    validator_module = import_module('.validators', package='sqvid')

    n_failed = 0

    for table in cfg[db_name]:
        for column in cfg[db_name][table]:
            for val in cfg[db_name][table][column]:
                validator_name = val['validator']
                args = val.get('args')

                validator_fn = getattr(validator_module, validator_name)
                r, k = execute_validation(engine, table, column, validator_fn,
                                          args)
                if len(r) == 0:
                    print("PASSED: Validation on [{}] {}.{} of {}{}".format(
                        db_name,
                        table,
                        column,
                        validator_name,
                        '({})'.format(args) if args else ''
                    ))
                else:
                    print("FAILED: Validation on [{}] {}.{} of {}{}".format(
                        db_name,
                        table,
                        column,
                        validator_name,
                        '({})'.format(args) if args else '',
                    ))
                    print("Offending {} rows:".format(len(r)))
                    print(NiceTable(list(map(tuple, r)), col_names=k))
                    n_failed += 1

    if n_failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)
