#!/usr/bin/env python2.5
#
# Copyright 2009 Bradley Heilbrun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Module for running batches aginst the remote_api interface. """

__author__ = "nurblieh@gmail.com (Bradley Heilbrun)"

import sys, os

BASE_DIR = '/usr/local/google_appengine/'
EXTRA_PATHS = [
  BASE_DIR,
  os.path.join(BASE_DIR, 'lib', 'antlr3'),
  os.path.join(BASE_DIR, 'lib', 'django'),
  os.path.join(BASE_DIR, 'lib', 'webob'),
  os.path.join(BASE_DIR, 'lib', 'yaml', 'lib'),
]

sys.path += EXTRA_PATHS

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db
import getpass

def auth_func():
  return (raw_input('Username:'), getpass.getpass('Password:'))

remote_api_stub.ConfigureRemoteDatastore('sf-trees', '/remote_api', auth_func)

