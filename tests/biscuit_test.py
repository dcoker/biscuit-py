#!/usr/bin/python
# coding=utf-8

import unittest

import biscuit
import os.path
import yaml


class TestBiscuit(unittest.TestCase):
    def test_algorithms(self):
        secrets = biscuit.biscuit()
        with open(os.path.join(os.path.dirname(__file__), "hello.yaml"), "r") as fp:
            parsed = yaml.load(fp)
            secrets.update(parsed)
        self.assertEqual("hello", secrets.get("aes"))
        self.assertEqual("hello", secrets.get("secretbox"))
        self.assertEqual("hello", secrets.get("none"))

    def test_region_from_arn(self):
        tests = {"arn:aws:kms:us-west-1:123456789012:key/37793df5-ad32-4d06-b19f-bfb95cee4a35": "us-west-1",
                 "key/37793df5-ad32-4d06-b19f-bfb95cee4a35": None,
                 "arn:aws:kms:us-west-1:123456789012:alias/biscuit-x": "us-west-1",
                 "alias/biscuit-x": None}
        for arn, region in tests.iteritems():
            self.assertEqual(region, biscuit.region_from_arn(arn))


if __name__ == '__main__':
    unittest.main()
