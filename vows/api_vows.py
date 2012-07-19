#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context

import re

storage_path = '/tmp/thumbor-vows/storage'
crocodile_file_path = abspath(join(dirname(__file__), 'crocodile.jpg'))
oversized_file_path = abspath(join(dirname(__file__), 'fixtures/image.jpg'))

#if exists(storage_path):
#    rmtree(storage_path)

class BaseContext(TornadoHTTPContext):
    def __init__(self, *args, **kw):
        super(BaseContext, self).__init__(*args, **kw)
        self.ignore('post_file', 'delete')

    def delete(self, path, data={}):
        return self.fetch(path, method="DELETE", body=[], allow_nonstandard_methods=True)

    def post_file(self, method, path, media_type, body):
        return self.fetch(path,
                          method=method.upper(),
                          body=body,
                          headers={
                              'Content-Type': media_type
                          },
                          allow_nonstandard_methods=True)


@Vows.batch
class UseAPIToPostAnImage(BaseContext):
    def get_app(self):
        cfg = Config()
        cfg.ENABLE_ORIGINAL_PHOTO_API = True
        cfg.ORIGINAL_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = storage_path
        cfg.ALLOW_ORIGINAL_PHOTO_DELETION = True
        cfg.ALLOW_ORIGINAL_PHOTO_PUTTING = True

        importer = Importer(cfg)
        importer.import_modules()
        ctx = Context(None, cfg, importer)
        application = ThumborServiceApp(ctx)
        return application


    class POSTAnImage(BaseContext):

        class WhenPostingAValidImageWithoutFilename(BaseContext):
            def topic(self):
                with open(crocodile_file_path, 'r') as croc:
                    body = croc.read()
                response = self.post_file('post', '/api', 'image/jpeg', body)
                return response

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    return response.code

                def should_be_201_created(self, topic):
                    expect(topic).to_equal(201)

            class Headers(TornadoHTTPContext):
                def topic(self, response):
                    return response.headers

                def should_set_a_correct_location(self, headers):
                    expect(headers).to_include('Location')
                    expect(headers['Location']).to_match(r'.*/api/[^\/]{36}')


        class WhenPostingAValidImageWithAFilename(BaseContext):
            def topic(self):
                with open(crocodile_file_path, 'r') as croc:
                    body = croc.read()
                response = self.post_file('post', '/api/crocodile.jpg', 'image/jpeg', body)
                return response

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    return response.code

                def should_be_201_created(self, topic):
                    expect(topic).to_equal(201)

            class Headers(TornadoHTTPContext):
                def topic(self, response):
                    return response.headers

                def should_set_a_location_containing_filename(self, headers):
                    expect(headers).to_include('Location')
                    expect(headers['Location']).to_match(r'.*/api/[^\/]{36}/crocodile.jpg')

        class WhenPostingAnInvalidImage(BaseContext):
            def topic(self):
                response = self.post_file('post', '/api', 'text/plain', 'invalid image')
                return response

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    return response.code

                def should_be_415_media_type_not_supported(self, topic):
                    expect(topic).to_equal(415)


    class PUTAnImage(BaseContext):

        class WhenPuttingAValidImage(BaseContext):
            def topic(self):
                with open(crocodile_file_path, 'r') as croc:
                    body = croc.read()
                response = self.post_file('post', '/api/crocodile.jpg', 'image/jpeg', body)
                uri = re.compile(".*(/api/.*)").search(response.headers['Location']).group(1);
                response = self.post_file('put', uri, 'image/jpeg', body)
                return response

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    print response
                    return response.code

                def should_be_200_ok(self, topic):
                    expect(topic).to_equal(200)

        class WhenPuttingAnInvalidImage(BaseContext):
            def topic(self):
                with open(crocodile_file_path, 'r') as croc:
                    body = croc.read()
                response = self.post_file('post', '/api/crocodile.jpg', 'image/jpeg', body)
                uri = re.compile(".*(/api/.*)").search(response.headers['Location']).group(1);
                response = self.post_file('put', uri, 'text/plain', 'invalid image')
                return response

            class StatusCode(TornadoHTTPContext):
                def topic(self, response):
                    return response.code

                def should_be_415_media_type_not_supported(self, topic):
                    expect(topic).to_equal(415)