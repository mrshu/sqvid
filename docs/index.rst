.. SQVID documentation master file, created by
   sphinx-quickstart on Tue Oct  8 16:24:27 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SQVID's documentation!
=================================

SQVID, the **Simple sQl Validator of varIous Datasources** is a framework
for validating any type of data source that can be queried via SQL with
`SQLAlchemy`_.

It aims to be a simplified and extensible counterpart to `validation of dbt
models`_ or `data assertions of dataform`_ that does not require you to use
the full `dbt`_ or `dataform`_ and still ensure your data is automatically
validated to be what you expect it to be. This allows SQVID to be used on
all sorts of data sources: from CSVs and spreadsheets to massive databases.

You can easily use SQVID to serve as a "sanity check" of your processing
pipeline or as a testing framework for your various ETL processes.

Installation
------------

.. code::

    pip install sqvid

-------------------

.. toctree::
   :maxdepth: 1
   :caption: Table of Contents:

   getting-started
   sqvid-config
   validators




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _validation of dbt models: https://docs.getdbt.com/docs/testing
.. _data assertions of dataform: https://docs.dataform.co/guides/assertions/
.. _dbt: https://getdbt.com
.. _dataform: https://dataform.co/

