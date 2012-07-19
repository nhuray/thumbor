#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import uuid

from thumbor.handlers import ContextHandler

class RestfulAPIHandler(ContextHandler):

    def post(self, filename):
        if self.validate():
            id = str(uuid.uuid4())
            if filename : id = id + '/' + filename
            body = self.request.body
            try:
                self.write_file(id, body)
                self.set_status(201)
                self.set_header('Location', self.location(id))
            except RuntimeError:
                self._error(500, 'Internal Server Error')

    def put(self, id):
        if not self.context.config.ALLOW_ORIGINAL_PHOTO_PUTTING: return
        if self.validate():
            body = self.request.body
            try:
                self.write_file(id, body)
                self.set_status(200)
            except RuntimeError:
                self._error(500, 'Internal Server Error')


    def delete(self, id):
        if not self.context.config.ALLOW_ORIGINAL_PHOTO_DELETION: return
        if self.context.modules.storage.exists(id):
            self.context.modules.storage.remove(id)

    def get(self, id):
        if self.context.modules.storage.exists(id):
            body = self.context.modules.storage.get(id)
            self.write(200, body)
        else:
            self._error(404, 'No original image was specified in the given URL')

    def validate(self):
        conf = self.context.config
        engine = self.context.modules.engine

        try:
            engine.load(self.request.body,None)
        except IOError:
            self._error(415, 'Unsupported Media Type')
            return False

        size = engine.size

        if (conf.MAX_SIZE != 0 and  len(self.request.body) > conf.MAX_SIZE):
            self._error(412, 'Precondition Failed : Image exceed max size')
            return False

        if (conf.MIN_WIDTH > size[0] or conf.MIN_HEIGHT > size[1]) :
            self._error(412, 'Precondition Failed : Image is too small')
            return False

        return True

    def write_file(self, id, body):
        storage = self.context.modules.original_photo_storage
        storage.put(id, body)

    def location(self, id):
        req = self.request
        return req.protocol + "://" + req.host + '/api/' + id