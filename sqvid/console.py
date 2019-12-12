from .executor import execute_validations
from nicetable.nicetable import NiceTable
import sys
import click

QUERY_VERBOSE_STR = "\nRUNNING QUERY:\n===========\n{}\n==========="


@click.command()
@click.option('--config',
              type=click.Path(exists=True),
              required=True,
              help='Path to a .toml config file.')
@click.option('--verbose/--no-verbose', default=False,
              help='Turn on verbose output of SQL queries.')
def run(config, verbose):
    """Validator of data that is queriable via SQL."""

    n_failed = 0
    for validation in execute_validations(config):
        if verbose:
            print(QUERY_VERBOSE_STR.format(validation['query']))

        print(validation['output'])

        if validation['result'] in ['failed', 'error']:
            n_failed += 1

        if validation['result'].startswith('failed'):
            print("Offending {} rows:".format(len(validation['rows'])))
            print(NiceTable(validation['rows'],
                            col_names=validation['col_names']))

    if n_failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)
