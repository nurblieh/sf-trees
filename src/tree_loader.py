#!/usr/bin/python2.5
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

"""Bulk uploader for SFTree entities, for use with appcfg.py upload_data.

The original data (in excel format) is available from,
http://datasf.org/story.php?title=street-tree-list

You'll need to convert the above to csv. I used NeoOffice. 

Example csv line,
1,City Maintained,"Pinus radiata :: Pine, Monterey",10 10th Ave,1,Median : Cutout,Tree,DPW,,,3,16,,-122.4689079859443294017005082,37.78675782522857080248498787

You'll also need to an external batch geo encoder to convert from the SPCS83
planar coordinates to lat/lon. I wrote my own."""

__author__ = 'nurblieh@gmail.com (Bradley Heilbrun)'

from google.appengine.ext import db
from google.appengine.tools import bulkloader
import datetime
import sys

sys.path.append('.')
import models

class TreeLoader(bulkloader.Loader):
  def __init__(self):
    def parse_date(x):
      if x:
        return datetime.datetime.strptime(x, '%m/%d/%Y').date()
      else:
        return None
       
    def str_to_geopt(latlon):
      """ latlon: latitude and longitude separated by ,"""
      lat, lon = [float(v) for v in latlon.split(',')]
      return db.GeoPt(lat, lon)
     
    dummy = lambda x: None
    
    bulkloader.Loader.__init__(self, 'SFTree',
                               [('ID', int),
                                ('legal_status', str),
                                ('species', str),
                                ('address', str),
                                ('tree_order', int),
                                ('site_type', str),
                                ('plant_type', str),
                                ('caretaker', str),
                                ('care_assistant', str),
                                ('planting_date', parse_date),
                                ('dbh', str),
                                ('plot_size', str),
                                ('permit_notes', str),
                                ('geoloc', str_to_geopt),
                                ('_dummy', dummy)]) # place holder
                    
                    
  def create_entity(self, values, key_name=None, parent=None):
    """This runs before the input data has been parsed by the loader."""
    
    # The app engine bulkloader does not provide a means for gracefully
    # combining two input fields into one output field. """
    values[13] = values[14] + ',' + values[13]
    # Original data provides a unique persistent ID field. So, we 
    # generate the appropriate native Key type based on this ID.
    key_name = db.Key.from_path('SFTrees', int(values[0])).name()
    return super(TreeLoader, self).create_entity(values, key_name)
  
  def handle_entity(self, entity):
    """Now that the entity is created. Generate and save the geoboxes."""
    entity.update_geoboxes()
    return entity


loaders = [TreeLoader]
                                
