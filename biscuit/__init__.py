# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import base64
import binascii
import logging
import sys

import boto3
import botocore
import botocore.exceptions
import libnacl.secret
from Cryptodome.Cipher import AES

KEY_ID_FIELD = "key_id"
CIPHERTEXT_FIELD = "ciphertext"
KEY_MANAGER_FIELD = "key_manager"
ALGORITHM_FIELD = "algorithm"

logger = logging.getLogger("biscuit")


def default_kms_factory(region):
    return boto3.client('kms', region_name=region)


def biscuit(kms_client_factory=default_kms_factory):
    """constructs a Biscuit with default settings.

    kms_client_factory is a function that accepts a region string and
    returns a boto3 KMS client."""
    algorithms = {
        'secretbox': SecretBoxAlgo(),
        'aesgcm256': AesGcm256Algo(),
        'none': PlainAlgo(),
    }
    managers = {
        'kms': AwsKmsKeyManager(kms_client_factory),
        'testing': TestingKeyManager()
    }
    return Biscuit(algorithms, managers)


class Biscuit:
    """Biscuit is a reader for encrypted secrets.

    Example:

        from biscuit import biscuit
        secrets = biscuit()
        secrets.read_yaml(open("secrets.yml", "r"))
        decrypted = secrets.get("launch_codes")
    """

    def __init__(self, algorithms, managers):
        """constructor.

        algorithms is a map of {name -> [algorithm, ...]}.
        managers is a map of {name -> [manager, ...]}.
        """
        self.algorithms = algorithms
        self.managers = managers
        self.entries = {}

    def update(self, entries):
        """update updates the internal list of entries with entries from
        the provided map.

        entries is a map of {name -> [value, ...]}.
        """
        self.entries.update(entries)
        return self

    def get(self, name):
        """get decrypts a single entry.

        if there are multiple entries for a name, the first one to
        successfully decrypt will be returned.

        if none of the entries are able to be decrypted, this method returns
        None.
        """
        for entry in self.entries[name]:
            try:
                algo = self.algorithms[entry[ALGORITHM_FIELD]]
                key = None
                if algo.requires_key():
                    key = self.managers[entry[KEY_MANAGER_FIELD]](name, entry)
                plaintext = algo(key, base64.decodestring(
                    entry[CIPHERTEXT_FIELD]))
                return plaintext
            except (ValueError,
                    binascii.Error,
                    botocore.exceptions.ClientError,
                    botocore.exceptions.BotoCoreError) \
                    as e:
                logger.warning("Error decrypting: %s", e)
                continue
        return None


class AwsKmsKeyManager:
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, name, value):
        client = self.factory(region_from_arn(value[KEY_ID_FIELD]))
        decrypt_key_response = client.decrypt(
            CiphertextBlob=base64.decodestring(value["key_ciphertext"]),
            EncryptionContext={'SecretName': name})
        return decrypt_key_response["Plaintext"]


class TestingKeyManager:
    def __call__(self, key, ciphertext):
        return ("x" * 32).encode('ascii')


class SecretBoxAlgo():
    def requires_key(self):
        return True

    def __call__(self, key, ciphertext):
        box = libnacl.secret.SecretBox(key)
        return box.decrypt(ciphertext)


class PlainAlgo():
    def requires_key(self):
        return False

    def __call__(self, _, ciphertext):
        return ciphertext


class AesGcm256Algo():
    def requires_key(self):
        return True

    def __call__(self, key, ciphertext):
        # format is (ciphertext, gcm_tag, nonce)
        nonce = ciphertext[-12:]
        ciphertext_no_nonce = ciphertext[:-12]
        gcm_tag = ciphertext_no_nonce[-16:]
        ciphertext_only = ciphertext_no_nonce[:-16]
        aes = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return aes.decrypt_and_verify(ciphertext_only, gcm_tag)


def region_from_arn(arn):
    if arn.startswith("arn:") and arn.split(":") > 6:
        return arn.split(":")[3]
    return None
