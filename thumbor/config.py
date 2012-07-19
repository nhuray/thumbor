#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from collections import defaultdict
import os
from os.path import join, exists, expanduser, dirname, abspath
import imp
import tempfile
from textwrap import fill

class ConfigurationError(RuntimeError):
    pass

class Config(object):
    class_defaults = {}
    class_group_items = defaultdict(list)
    class_groups = []
    class_descriptions = {}

    @classmethod
    def define(cls, key, value, description, group='General'):
        cls.class_defaults[key] = value
        cls.class_descriptions[key] = description
        cls.class_group_items[group].append(key)
        if not group in cls.class_groups:
            cls.class_groups.append(group)

    @classmethod
    def get_conf_file(cls):
        lookup_conf_file_paths = [
            os.curdir,
            expanduser('~'),
            '/etc/',
            dirname(__file__)
        ]
        for conf_path in lookup_conf_file_paths:
            conf_path_file = abspath(join(conf_path, 'thumbor.conf'))
            if exists(conf_path_file):
                return conf_path_file

        raise ConfigurationError('thumbor.conf file not passed and not found on the lookup paths %s' % lookup_conf_file_paths)

    @classmethod
    def load(cls, path):
        if path is None:
            path = cls.get_conf_file()

        with open(path) as config_file:
            name='configuration'
            code = config_file.read()
            module = imp.new_module(name)
            exec code in module.__dict__

            conf = cls()
            conf.config_file = path
            for name, value in module.__dict__.iteritems():
                setattr(conf, name, value)

            return conf

    def __init__(self, **kw):
        if 'defaults' in kw:
            self.defaults = kw['defaults']

        for key, value in kw.iteritems():
            setattr(self, key, value)

    def validates_presence_of(self, *args):
        for arg in args:
            if not hasattr(self, arg):
                raise ConfigurationError('Configuration %s was not found and does not have a default value. Please verify your thumbor.conf file' % arg)

    def get(self, name, default=None):
        if hasattr(self, name):
            return getattr(self, name)
        return default

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        if 'defaults' in self.__dict__ and name in self.__dict__['defaults']:
            return self.__dict__['defaults'][name]

        if name in Config.class_defaults:
            return Config.class_defaults[name]

        raise AttributeError(name)

Config.define('MAX_WIDTH', 0, "Max width in pixels for images read or generated by thumbor", 'Imaging')
Config.define('MAX_HEIGHT', 0, "Max height in pixels for images read or generated by thumbor", 'Imaging')
Config.define('MIN_WIDTH', 1, "Min width in pixels for images read or generated by thumbor", 'Imaging')
Config.define('MIN_HEIGHT', 1, "Min width in pixels for images read or generated by thumbor", 'Imaging')
Config.define('ALLOWED_SOURCES', [], "Allowed domains for the http loader to download. These are regular expressions.", 'Imaging')
Config.define('QUALITY', 80, 'Quality index used for generated JPEG images', 'Imaging')
Config.define('MAX_AGE', 24 * 60 * 60, 'Max AGE sent as a header for the image served by thumbor in seconds', 'Imaging')
Config.define('MAX_AGE_TEMP_IMAGE', 0, "Indicates the Max AGE header in seconds for temporary images (images that haven't been detected yet)", 'Imaging')
Config.define('RESPECT_ORIENTATION', False, 'Indicates whether thumbor should rotate images that have an Orientation EXIF header', 'Imaging')

Config.define('LOADER',  'thumbor.loaders.http_loader', 'The loader thumbor should use to load the original image. This must be the full name of a python module (python must be able to import it)', 'Extensibility')
Config.define('STORAGE', 'thumbor.storages.file_storage', 'The file storage thumbor should use to store original images. This must be the full name of a python module (python must be able to import it)', 'Extensibility')
Config.define('RESULT_STORAGE', None, 'The result storage thumbor should use to store generated images. This must be the full name of a python module (python must be able to import it)', 'Extensibility')
Config.define('ENGINE', 'thumbor.engines.pil', 'The imaging engine thumbor should use to perform image operations. This must be the full name of a python module (python must be able to import it)', 'Extensibility')

Config.define('SECURITY_KEY', 'MY_SECURE_KEY', 'The security key thumbor uses to sign image URLs', 'Security')

Config.define('ALLOW_UNSAFE_URL', True, 'Indicates if the /unsafe URL should be available', 'Security')
Config.define('ALLOW_OLD_URLS', True, 'Indicates if encrypted (old style) URLs should be allowed', 'Security')

# FILE LOADER OPTIONS
Config.define('FILE_LOADER_ROOT_PATH', '/tmp', 'The root path where the File Loader will try to find images', 'File Loader')

# HTTP LOADER OPTIONS
Config.define('MAX_SOURCE_SIZE', 0, "Max size in Kb for images downloaded by thumbor's HTTP Loader", 'HTTP Loader')
Config.define('REQUEST_TIMEOUT_SECONDS', 120, "Maximum number of seconds to wait for an original image to download", 'HTTP Loader')

# FILE STORAGE GENERIC OPTIONS
Config.define('STORAGE_EXPIRATION_SECONDS', 60 * 60 * 24 * 30, "Expiration in seconds for the images in the File Storage. Defaults to one month", 'File Storage') # default one month
Config.define('STORES_CRYPTO_KEY_FOR_EACH_IMAGE', False, 'Indicates whether thumbor should store the signing key for each image in the file storage. This allows the key to be changed and old images to still be properly found', 'File Storage')

# FILE STORAGE OPTIONS
Config.define('FILE_STORAGE_ROOT_PATH', join(tempfile.gettempdir(), 'thumbor', 'storage'), 'The root path where the File Storage will try to find images', 'File Storage')

# PHOTO API / UPLOAD OPTIONS
Config.define('MAX_SIZE', 0, "Max size in Kb for images uploaded to thumbor", 'Upload')
Config.define('ENABLE_ORIGINAL_PHOTO_UPLOAD', False, 'Indicates whether thumbor should enable File uploads', 'Upload')
Config.define('ENABLE_ORIGINAL_PHOTO_API', False, 'Indicates whether thumbor should enable photos Rest API', 'Upload')
Config.define('ORIGINAL_PHOTO_STORAGE', 'thumbor.storages.file_storage', 'The type of storage to store uploaded images with', 'Upload')
Config.define('ALLOW_ORIGINAL_PHOTO_DELETION', False, 'Indicates whether image deletion should be allowed', 'Upload')
Config.define('ALLOW_ORIGINAL_PHOTO_PUTTING', False, 'Indicates whether image overwrite should be allowed', 'Upload')


# MONGO STORAGE OPTIONS
Config.define('MONGO_STORAGE_SERVER_HOST', 'localhost', 'MongoDB storage server host', 'MongoDB Storage')
Config.define('MONGO_STORAGE_SERVER_PORT', 27017, 'MongoDB storage server port', 'MongoDB Storage')
Config.define('MONGO_STORAGE_SERVER_DB', 'thumbor', 'MongoDB storage server database name', 'MongoDB Storage')
Config.define('MONGO_STORAGE_SERVER_COLLECTION', 'images', 'MongoDB storage image collection', 'MongoDB Storage')

# REDIS STORAGE OPTIONS
Config.define('REDIS_STORAGE_SERVER_HOST', 'localhost', 'Redis storage server host', 'Redis Storage')
Config.define('REDIS_STORAGE_SERVER_PORT', 6379, 'Redis storage server port', 'Redis Storage')
Config.define('REDIS_STORAGE_SERVER_DB', 0, 'Redis storage database index', 'Redis Storage')
Config.define('REDIS_STORAGE_SERVER_PASSWORD', None, 'Redis storage server password', 'Redis Storage')

# MIXED STORAGE OPTIONS
Config.define('MIXED_STORAGE_FILE_STORAGE', 'thumbor.storages.no_storage', 'Mixed Storage file storage. This must be the full name of a python module (python must be able to import it)', 'Mixed Storage')
Config.define('MIXED_STORAGE_CRYPTO_STORAGE', 'thumbor.storages.no_storage', 'Mixed Storage signing key storage. This must be the full name of a python module (python must be able to import it)', 'Mixed Storage')
Config.define('MIXED_STORAGE_DETECTOR_STORAGE', 'thumbor.storages.no_storage', 'Mixed Storage detector information storage. This must be the full name of a python module (python must be able to import it)', 'Mixed Storage')

# JSON META ENGINE OPTIONS
Config.define('META_CALLBACK_NAME', None, 'The callback function name that should be used by the META route for JSONP access', 'Meta')

# DETECTORS OPTIONS
Config.define('DETECTORS', [], 'List of detectors that thumbor should use to find faces and/or features. All of them must be full names of python modules (python must be able to import it)', 'Detection')

# FACE DETECTOR CASCADE FILE
Config.define('FACE_DETECTOR_CASCADE_FILE', 'haarcascade_frontalface_alt.xml', 'The cascade file that opencv will use to detect faces', 'Detection')

# AVAILABLE FILTERS
Config.define('FILTERS', [], 'List of filters that thumbor will allow to be used in generated images. All of them must be full names of python modules (python must be able to import it)', 'Filters')

# RESULT STORAGE
Config.define('RESULT_STORAGE_EXPIRATION_SECONDS', 0, 'Expiration in seconds of generated images in the result storage', 'Result Storage') # Never expires
Config.define('RESULT_STORAGE_FILE_STORAGE_ROOT_PATH', join(tempfile.gettempdir(), 'thumbor', 'result_storage'), 'Path where the Result storage will store generated images', 'Result Storage')
Config.define('RESULT_STORAGE_STORES_UNSAFE', False, 'Indicates whether unsafe requests should also be stored in the Result Storage', 'Result Storage')

# QUEUED DETECTOR REDIS OPTIONS
Config.define('REDIS_QUEUE_SERVER_HOST', 'localhost', 'Server host for the queued redis detector', 'Queued Redis Detector')
Config.define('REDIS_QUEUE_SERVER_PORT', 6379, 'Server port for the queued redis detector', 'Queued Redis Detector')
Config.define('REDIS_QUEUE_SERVER_DB', 0, 'Server database index for the queued redis detector', 'Queued Redis Detector')
Config.define('REDIS_QUEUE_SERVER_PASSWORD', None, 'Server password for the queued redis detector', 'Queued Redis Detector')

def generate_config():
    MAX_LEN = 80
    SEPARATOR = '#'
    for group in Config.class_groups:
        keys = Config.class_group_items[group]
        sep_size = int(round((MAX_LEN - len(group)) / 2, 0)) - 1
        group_name = SEPARATOR * sep_size + ' ' + group + ' ' + SEPARATOR * sep_size
        if len(group_name) < MAX_LEN:
            group_name += SEPARATOR
        print group_name
        for key in keys:
            print
            value = Config.class_defaults[key]
            description = Config.class_descriptions[key]

            wrapped = fill(description, width=78, subsequent_indent='## ')

            print '## %s' % wrapped
            print '## Defaults to: %s' % value
            print '#%s = %s' % (key, format_value(value))
        print
        print SEPARATOR * MAX_LEN
        print
        print

def format_value(value):
    if isinstance(value, basestring):
        return "'%s'" % value
    if isinstance(value, (tuple, list, set)):
        representation = '[\n'
        for item in value:
            representation += '#    %s' % item
        representation += '#]'
        return representation
    return value

if __name__ == '__main__':
    generate_config()
