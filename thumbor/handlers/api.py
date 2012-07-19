#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import urllib
import uuid

from thumbor.handlers import ContextHandler

class RestfulAPIHandler(ContextHandler):

    def post(self, filename):
        if filename != None: return
        if self.validate():
            filename = uuid.uuid4()
            body = self.request.body
            try:
               self.write_file(filename, body)
               self.set_status(201)
               self.set_header('Location', self.request.uri + '/' + filename)
            except RuntimeError:
               self._error(500, 'Internal Server Error')
        else:
            self._error(412, 'File is too big, not an image or too small image')


    def put(self, filename):
        if not self.context.config.ALLOW_ORIGINAL_PHOTO_PUTTING: return
        if self.validate():
            body = self.request.body
            try:
               self.write_file(filename, body)
               self.set_status(200)
            except RuntimeError:
               self._error(500, 'Internal Server Error')
        else:
            self._error(412, 'File is too big, not an image or too small image')

    def delete(self, filename):
        if not self.context.config.ALLOW_ORIGINAL_PHOTO_DELETION: return
        if self.context.modules.storage.exists(filename):
            self.context.modules.storage.remove(filename)

    def get(self, filename):
       if self.context.modules.storage.exists(filename):
           body = self.context.modules.storage.get(filename)
           self.write(200, body)
       else:
           self._error(404, 'No original image was specified in the given URL')



    def write_file(self, filename, body):
        storage = self.context.modules.original_photo_storage
        storage.put(filename, body)

    def validate(self):
        conf = self.context.config
        engine = self.context.modules.engine

        if ( conf.MAX_SIZE != 0 and  len(self.request.body) > conf.MAX_SIZE ):
            return False

        try:
            engine.load(self.request.body,None)
        except IOError:
            return False

        size = engine.size
        if (conf.MIN_WIDTH > size[0] or conf.MIN_HEIGHT > size[1]) :
            return False

        return True
