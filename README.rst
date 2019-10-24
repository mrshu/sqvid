SQVID
=====

.. image:: https://img.shields.io/pypi/v/sqvid.svg
    :target: https://pypi.python.org/pypi/sqvid
    :alt: PyPI Status

.. image:: https://img.shields.io/travis/mrshu/sqvid.svg
    :target: https://travis-ci.org/mrshu/sqvid
    :alt: Build Status

.. image:: https://coveralls.io/repos/github/mrshu/sqvid/badge.svg?branch=master
    :target: https://coveralls.io/github/mrshu/sqvid?branch=master
    :alt: Code coverage Status

.. image:: https://img.shields.io/pypi/l/sqvid.svg
   :target: ./LICENSE
   :alt: License Status

.. image:: https://readthedocs.org/projects/sqvid/badge/?version=latest
   :target: https://sqvid.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


SQVID, the Simple sQl Validator of varIous Datasources is a framework for
validating any type of data source that can be queried via SQL with the
help of `SQLAlchemy`_. It aims to be a simplified and extensible
counterpart to `validation of dbt models`_ or `data assertions of
dataform`_ that does not require you to use the full `dbt`_ or `dataform`_
and still ensure your data is automatically validated to be what you expect
it to be. This allows SQVID to be used on all sorts of data sources: from
CSVs and spreadsheets to massive databases.

You can easily use SQVID to serve as a "sanity check" of your processing
pipeline or as a testing framework for your various ETL processes.

Found out more about it in the `documentation`_.

Installation
------------

.. code::

    pip install sqvid

Example
-------

Let us consider a database table called ``suppliers`` that would result
from executing the following code snippet in a SQLite database called
``test_sqvid_db``.

.. code:: sql

    CREATE TABLE `suppliers` (
      `SupplierID` int NOT NULL,
      `SupplierName` varchar(255) DEFAULT NULL,
      `ContactName` varchar(255) DEFAULT NULL,
      `Address` varchar(255) DEFAULT NULL,
      `City` varchar(255) DEFAULT NULL,
      `PostalCode` varchar(255) DEFAULT NULL,
      `Country` varchar(255) DEFAULT NULL,
      `Phone` varchar(255) DEFAULT NULL
    );
    
    INSERT INTO `suppliers` (`SupplierID`, `SupplierName`, `ContactName`, `Address`, `City`, `PostalCode`, `Country`, `Phone`) VALUES
    (1, "Exotic Liquid", "Charlotte Cooper", "49 Gilbert St.", "Londona", "EC1 4SD", "UK", "(171) 555-2222"),
    (2, "New Orleans Cajun Delights", "Shelley Burke", "P.O. Box 78934", "New Orleans", "70117", "USA", "(100) 555-4822"),
    (3, "Grandma Kelly's Homestead", "Regina Murphy", "707 Oxford Rd.", "Ann Arbor", "48104", "USA", "(313) 555-5735"),
    (4, "Tokyo Traders", "Yoshi Nagase", "9-8 Sekimai Musashino-shi", "Tokyo", "100", "Japan", "(03) 3555-5011"),
    (5, "Cooperativa de Quesos 'Las Cabras'", "Antonio del Valle Saavedra", "Calle del Rosal 4", "Oviedo", "33007", "Spain", "(98) 598 76 54"),


In order to validate that this table contains the data we would expect it
to, we can put together the following SQVID validation config:

.. code:: toml

   [general]
   sqla = "sqlite:///test_sqvid_db.sqlite"
   db_name = 'test_sqvid_db'
   
   [[test_sqvid_db.suppliers.SupplierID]]
   validator = 'unique'
   
   [[test_sqvid_db.suppliers.SupplierID]]
   validator = 'in_range'
   args = {min = 1, max = 256}

*Note that the the validation config file is formated using* `TOML`_ *-- you
can find a very nice tutorial on this formatting language at*
`LearnXinYMinutes`_.

The ``[general]`` section specifies SQLAlchemy connection string in
``sqla`` and the name of the DB that is going to have its data validated in
``db_name``.

The other sections specify the various validations performed on this DB. In
particular the table ``suppliers`` and data in its column ``SupplierID`` is
being validated via two validators: the ``unique`` validator ensures that
each value in this column occurs only once and the ``in_range`` validator
checks whether all data points in this column fall withing the ``min`` and
``max`` range specified via parameters of the same name in ``args``.

Once we save a validation config like this one into a file (say
``validate_suppliers.toml``), SQVID validation tests can be invoked in the
following way:

.. code::
    
    sqvid --config ./validate_suppliers.toml

This should provide output close to the following:

.. code::

    PASSED: Validation on [test_sqvid_db] suppliers.SupplierID of unique
    PASSED: Validation on [test_sqvid_db] suppliers.SupplierID of in_range({'min': 1, 'max': 256})

Since all tests passed, ``sqvid`` would finish with exit code ``0``.

Failing validations
~~~~~~~~~~~~~~~~~~~

What happens when a SQVID validation test fails? We can easily see that by
slightly changing the config file from the above:

.. code:: toml

   [general]
   sqla = "sqlite:///test_sqvid_db.sqlite"
   db_name = 'test_sqvid_db'
   
   [[test_sqvid_db.suppliers.SupplierID]]
   validator = 'unique'
   
   [[test_sqvid_db.suppliers.SupplierID]]
   validator = 'in_range'
   args = {min = 3, max = 256}


Note that the contents stayed the same, except for the final line where the
``min`` parameter has been set to ``3``. If we now save this file (to say
``./validate_suppliers_fail.toml``), we can again execute SQVID tests in a
similar way:

.. code::
    
    sqvid --config ./validate_suppliers_fail.toml

The output should change to something like this:

.. code::

    PASSED: Validation on [test_sqvid_db] suppliers.SupplierID of unique
    FAILED: Validation on [test_sqvid_db] suppliers.SupplierID of in_range({'min': 3, 'max': 256})
    Offending 2 rows:
    +--------------+------------------------------+--------------------+------------------+---------------+--------------+-----------+------------------+
    |  SupplierID  |  SupplierName                |  ContactName       |  Address         |  City         |  PostalCode  |  Country  |  Phone           |
    +--------------+------------------------------+--------------------+------------------+---------------+--------------+-----------+------------------+
    |           1  |  Exotic Liquid               |  Charlotte Cooper  |  49 Gilbert St.  |  Londona      |  EC1 4SD     |  UK       |  (171) 555-2222  |
    |           2  |  New Orleans Cajun Delights  |  Shelley Burke     |  P.O. Box 78934  |  New Orleans  |  70117       |  USA      |  (100) 555-4822  |
    +--------------+------------------------------+--------------------+------------------+---------------+--------------+-----------+------------------+


As we would expect, the ``unique`` validation still passed while the
``in_range`` validation failed on the two rows which have their
``SupplierID`` outside of the ``[3, 256]`` range.

Since some tests failed, ``sqvid`` would finish with exit code ``1``.

Tests
-----

As this project makes use of `Poetry <https://poetry.eustace.io/>`_, after
installing it the tests can be ran by executing the following from the
project's root directory:

.. code:: bash

    poetry run pytest

They can also be ran with `coverage <https://nose.readthedocs.io/en/latest/plugins/cover.html>`_:

.. code:: bash

    poetry run pytest --cov=sqvid


License
-------

Copyright 2019 Marek "mr.Shu" Suppa

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.



.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _validation of dbt models: https://docs.getdbt.com/docs/testing
.. _data assertions of dataform: https://docs.dataform.co/guides/assertions/
.. _dbt: https://getdbt.com
.. _dataform: https://dataform.co/
.. _TOML: https://github.com/toml-lang/toml
.. _LearnXinYMinutes:  https://learnxinyminutes.com/docs/toml/
.. _documentation:  https://sqvid.readthedocs.io/
