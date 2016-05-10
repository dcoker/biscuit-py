==========
biscuit-py
==========

.. image:: https://img.shields.io/pypi/v/biscuit-py.svg?maxAge=600   :target:

Biscuit provides tooling for securely managing secrets used in AWS
deployments. This project implements example Python code for reading secrets
encrypted with the `Biscuit CLI <https://github.com/dcoker/biscuit>`_.

----------
Installing
----------

Install with::

    $ pip install biscuit-py

-------
Example
-------

::

    from biscuit import biscuit

    secrets = biscuit()
    with open("secrets.yml", "r") as fp:
        secrets.update(yaml.safe_load(fp))
    launch_codes = secrets.get("launch_codes")

You can also control the creation/pooling of the AWS KMS client by passing a factory method to ``biscuit()``::

    secrets = biscuit(lambda region: boto3.client('kms', region_name=region))
