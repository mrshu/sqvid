The SQVID config file
=====================

Every SQVID config file has basically two components: the ``[general]``
section and all the other sections that describe the configuration of
respective validations.


The ``[general]`` section
~~~~~~~~~~~~~~~~~~~~~~~~~

This section is generally used to set up parameters that affect all
validations that are defined in a single SQVID config file.

A sample ``[general]`` section may look as follows:

.. code:: toml

  [general]
  sqla = "sqlite:///test_sqvid_db.sqlite"
  db_name = 'test_sqvid_db'


``sqla``
    This parameter sets the so called `Database URL`_ that SQLAlchemy uses
    to connect to the database in which the data to be validated is located.

``db_name``
    The name of the database in which the data to be validated is located.
    Although some connection engines would already have this specified in
    the ``sqla`` parameter, having it specified separately allows us much
    greater flexibility when generating validations.


Definition of validations
~~~~~~~~~~~~~~~~~~~~~~~~~

Using the ``db_name`` mentioned above, validations are defined as arrays of
`TOML tables`_ in the format of ``$db_name.$table_name.$column_name``. Here
is a simple example:

.. code:: toml

  [[test_sqvid_db.suppliers.SupplierID]]
  validator = 'unique'

As we can see the ``$db_name`` would in this case be ``test_sqvid_db``, the
``suppliers`` would be the ``$table_name`` and ``SupplierID`` the
``$column_name``.

.. note::

  the double brackets (that is ``[[`` and ``]]``) around
  ``test_sqvid_db.suppliers.SupplierID`` denote "arrays of tables".  It
  means that ``test_sqvid_db.suppliers.SupplierID`` will not be a single
  table but rather an array. Among other things this allows us to define
  various validations for a single column. Here is a quick example:

  .. code:: toml

    [[test_sqvid_db.suppliers.SupplierID]]
    validator = 'unique'

    [[test_sqvid_db.suppliers.SupplierID]]
    validator = 'in_range'
    args = {min = 1, max = 256}

  This example defines two validations on the
  ``test_sqvid_db.suppliers.SupplierID`` column: one with the ``unique``
  validator and one with the ``in_range`` validator.

Once the database, table and column in which the data we want to validate
is define, we can specify which validator to use and with what parameters.
This can be done using he following set of parameters:

``validator``
    This (string) parameter needs to contain one of the validators
    described in :doc:`validators`. For example:

    .. code:: toml

      [[test_sqvid_db.suppliers.SupplierID]]
      validator = 'unique'

``args``
    Arguments to be passed to the specified validator. They expressed as a
    TOML table and TOML supports various ways of describing those. All of
    the following definitions are functionally equal:

    .. code:: toml

      [[test_sqvid_db.suppliers.SupplierID]]
      validator = 'in_range'
      args = {min = 1, max = 256}

      # is equivalent to

      [[test_sqvid_db.suppliers.SupplierID]]
      validator = 'in_range'
      args.min = 1
      args.max = 256

      # is again equivalen to

      [[test_sqvid_db.suppliers.SupplierID]]
      validator = 'in_range'

        [test_sqvid_db.suppliers.SupplierID.args]
        min = 1
        max = 256

    For short arguments (and short values) the first way is preferable. In
    all other cases the second one should make a bit more sense, especially
    in terms of readability.

``custom_column``
    Validating a single columns is sometimes of little use as what we would
    really want to validate is result of combining multiple columns.  That
    is exactly what ``custom_column`` is for: it allows for any custom SQL
    to be considered a "virtual" column onto which a validation can then be
    applied.

    Suppose we would like to check whether the combination of the
    ``SupplierID`` and ``SupplierName`` is unique. We can easily do that
    using the ``custom_column`` parameter as in the example below:

    .. code:: toml

      [[test_sqvid_db.suppliers.SupplierID]]
      validator = 'unique'
      custom_column = "SupplierID || '-' || SupplierName"

``severity``
    A "severity" of a validation defines what happens when it fails. It can
    be set to either ``error`` (the default) or ``warn``.  When set to
    ``warn``, the validation will still report the results (i.e. which rows
    did not meet the validation criteria) but the validation will otherwise
    behave as if it passed.

.. _Database URL: https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls
.. _TOML tables: https://github.com/toml-lang/toml#user-content-table
