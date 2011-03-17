#!/usr/bin/env python
#-*- coding: utf8 -*-

import unittest
import sys
from os.path import join, abspath, dirname

sys.path.append(abspath(join(dirname(__file__), '..')))

from tornado.testing import AsyncHTTPTestCase
from thumbor.app import ThumborServiceApp


class ThumborServiceTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp()

    def test_app_exists_and_is_instanceof_thumborserviceapp(self):
        assert isinstance(self._app, ThumborServiceApp), 'App does not exist or is not instance of the ThumborServiceApp class'
    
