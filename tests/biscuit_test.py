#!/usr/bin/python
# coding=utf-8

import binascii
import collections
import unittest

import biscuit
import os.path
import yaml

test_vector = collections.namedtuple('test_vector',
                                     ['key', 'nonce', 'plaintext', 'result'])


class TestAesGcm256(unittest.TestCase):
    # Test vectors taken from https://golang.org/src/crypto/cipher/gcm_test.go
    vectors = [
        test_vector(
            '11754cd72aec309bf52f7687212e8957',
            '3c819d9a9bed087615030b65',
            '',
            '250327c674aaf477aef2675748cf6971'
        ),
        test_vector(
            'ca47248ac0b6f8372a97ac43508308ed',
            'ffd2b598feabc9019262d2be',
            '',
            '60d20404af527d248d893ae495707d1a',
        ),
        test_vector(
            '7fddb57453c241d03efbed3ac44e371c',
            'ee283a3fc75575e33efd4887',
            'd5de42b461646c255c87bd2962d3b9a2',
            '2ccda4a5415cb91e135c2a0f78c9b2fdb36d1df9b9d5e596f83e8b7f52971cb3',
        )
    ]

    def test_vectors(self):
        method = biscuit.AesGcm256Algo()

        for v in self.vectors:
            key = binascii.unhexlify(v.key)
            plaintext = binascii.unhexlify(v.plaintext)
            ciphertext = binascii.unhexlify(v.result + v.nonce)
            self.assertEqual(plaintext, method(key, ciphertext))


class TestBiscuit(unittest.TestCase):
    def test_algorithms(self):
        secrets = biscuit.biscuit()
        with open(os.path.join(os.path.dirname(__file__),
                               "hello.yaml"), "r") as fp:
            parsed = yaml.load(fp)
            secrets.update(parsed)
        self.assertEqual("hello", secrets.get("aes"))
        self.assertEqual("hello", secrets.get("secretbox"))
        self.assertEqual("hello", secrets.get("none"))

    def test_region_from_arn(self):
        prefix = "arn:aws:kms:us-west-1:123456789012:"
        tests = {
            prefix + "key/37793df5-ad32-4d06-b19f-bfb95cee4a35": "us-west-1",
            "key/37793df5-ad32-4d06-b19f-bfb95cee4a35": None,
            prefix + "alias/biscuit-x": "us-west-1",
            "alias/biscuit-x": None}
        for arn, region in tests.iteritems():
            self.assertEqual(region, biscuit.region_from_arn(arn))


if __name__ == '__main__':
    unittest.main()
