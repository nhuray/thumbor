#!/usr/bin/env python
#-*- coding: utf8 -*-

import unittest
import sys
from os.path import join, abspath, dirname

sys.path.append(abspath(join(dirname(__file__), '..')))

from cStringIO import StringIO
from PIL import Image
from tornado.testing import AsyncHTTPTestCase

from thumbor.app import ThumborServiceApp

get_conf_path = lambda filename: abspath(join(dirname(__file__), 'fixtures', filename))

class MainHandlerDomainTest(AsyncHTTPTestCase):
    
    def get_app(self):
        return ThumborServiceApp(get_conf_path('conf.py'))

    def test_validates_passed_url_is_in_valid_domains(self):
        self.http_client.fetch(self.get_url('/www.mydomain.com/logo1.jpg'), self.stop)
        response = self.wait()
        self.assertEqual(404, response.code)
        self.assertEqual('Your domain is not allowed!', response.body)
        

class MainHandlerSourcePathTest(AsyncHTTPTestCase):
    
    def get_app(self):
        return ThumborServiceApp(get_conf_path('conf1.py'))
    
    def test_validates_passed_url_is_in_valid_source(self):
        self.http_client.fetch(self.get_url('/www.mydomain.com/logo2.jpg'), self.stop)
        response = self.wait()
        self.assertEqual(404, response.code)
        self.assertEqual('Your image source is not allowed!', response.body)


class MainHandlerTest(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp()

    def test_returns_success_status_code(self):
        self.http_client.fetch(self.get_url('/www.globo.com/media/globocom/img/sprite1.png'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)


class ImageTestCase(AsyncHTTPTestCase):

    def get_app(self):
        return ThumborServiceApp()

    def fetch_image(self, url):
        self.http_client.fetch(self.get_url(url), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        return Image.open(StringIO(response.body))


class MainHandlerImagesTest(ImageTestCase):

    def test_resizes_the_passed_image(self):
        image = self.fetch_image('/200x300/www.globo.com/media/globocom/img/sprite1.png')
        img_width, img_height = image.size
        self.assertEqual(img_width, 200)
        self.assertEqual(img_height, 300)

    def test_flips_horizontaly_the_passed_image(self):
        image = self.fetch_image('/www.globo.com/media/common/img/estrutura/borderbottom.gif')
        image_flipped = self.fetch_image('/-3x/www.globo.com/media/common/img/estrutura/borderbottom.gif')
        pixels = list(image.getdata())
        pixels_flipped = list(image_flipped.getdata())

        self.assertEqual(len(pixels), len(pixels_flipped), 'the images do not have the same size')

        reversed_pixels_flipped = list(reversed(pixels_flipped))

        self.assertEqual(pixels, reversed_pixels_flipped, 'did not flip the image')


if __name__ == '__main__':
    unittest.main()