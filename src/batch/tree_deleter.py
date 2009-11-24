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

""" Delete all SFTree entities in datastore. """

__author__ = "nurblieh@gmail.com (Bradley Heilbrun)"

import sys
import remote_client
from google.appengine.ext import db


sys.path.append('../')
from models import SFTree

def main():
  q = SFTree.all(keys_only=True)
  r = q.fetch(100)
  while len(r) > 0:
    print "Deleting %s through %s..." % (r[0].id(), r[-1].id())
    db.delete(r)
    r = q.fetch(100)
    
if __name__ == '__main__':
  main()