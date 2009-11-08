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

"""Primary module for handling sf-trees requests via Google App Engine."""

__author__ = "nurblieh@gmail.com (Bradley Heilbrun)"

import csv
import logging
import os
import urllib

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

import models
import geobox

LOCALHOST_MAPS_API_KEY = 'ABQIAAAAVC2WXXt_MSwCcbASK6sx1BT2yXp_ZAY8_\
ufC3CFXhHIE1NvwkxQouw5yaDOxD_Ek6CmtYpmX2FZZxA'

# List of resolutions and slices. Should be in increasing order of size/scope.
GEOBOX_CONFIGS = (
  (4, 5, True),
  (3, 2, True),
  (3, 8, False),
  (3, 16, False),
  (2, 5, False),
)

def build_geoboxes(lat, lon):
  """Returns a list of rectangles (defined by a list of coordinates) to overlay on maps."""
  geoboxes = []
  for params in GEOBOX_CONFIGS[:3]:
    resolution, slice, unused = params
    box = geobox.compute_tuple(lat, lon, resolution, slice)
    geoboxes.append(((box[0],box[1]),
                     (box[0],box[3]),
                     (box[2],box[3]),
                     (box[2],box[1])))
  return geoboxes
    
def geocode_address(address):
  """Geocode a street address into latitude, longitude."""
  lat, lon = None, None
  url = "http://maps.google.com/maps/geo?"
  url += urllib.urlencode((('q', address),
                          ('key', LOCALHOST_MAPS_API_KEY),
                          ('output', 'csv'),
                          ('sensor', 'false')))
  result = urlfetch.fetch(url)
  if result.status_code == 200:
    logging.info('geocode result: ' + result.content)
    for row in csv.reader([result.content]):
      lat,lon = row[2], row[3]
      break
  else:
    logging.error("%s [%s] : %s" % (url, result.status_code, result.content))

  return lat, lon


class MainPage(webapp.RequestHandler):
  """Handed to WSGIApplication. Responsible for all sf-trees pages."""
  def get(self):
    self.run()

  def post(self):
    self.run()

  def run(self):
    templates_path = os.path.dirname(__file__)
    index_tmpl = os.path.join(templates_path, 'index.html')
    
    address = self.request.get('address')
    # FIXME: tmpl defaults 
    trees, lat, lon, zoom, geoboxes = None, None, None, 12, None
    if address:
      # Geocode the user's request.
      lat,lon = geocode_address(address)
      # Temporary, so I can visualize the geoboxes.
      geoboxes = build_geoboxes(lat, lon)
      # Find the nearest 100 trees.
      results = models.SFTree.query(lat, lon, 100, (2,0))
      trees = [r[1] for r in results]
      zoom = 16

    tmpl_vars = { 'address': address,
                  'trees': trees,
                  'lat': lat,
                  'lon': lon,
                  'zoom': zoom,
                  'geoboxes': geoboxes
                  }
    logging.info('tmpl_vars: %s' % tmpl_vars)
    self.response.out.write(template.render(index_tmpl,tmpl_vars))


application = webapp.WSGIApplication([('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
