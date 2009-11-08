import logging
import math
from datetime import datetime

from google.appengine.ext import db

import geobox


def _earth_distance(lat1, lon1, lat2, lon2):
  RADIUS = 3963.1676
  lat1, lon1 = math.radians(float(lat1)), math.radians(float(lon1))
  lat2, lon2 = math.radians(float(lat2)), math.radians(float(lon2))
  return RADIUS * math.acos(math.sin(lat1) * math.sin(lat2) +
      math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1))


class SFTree(db.Model):
  """SFTree entity datatype."""
  legal_status = db.StringProperty()
  species = db.StringProperty()
  address = db.StringProperty()
  tree_order = db.IntegerProperty()
  site_type = db.StringProperty()
  plant_type = db.StringProperty()
  caretaker = db.StringProperty()
  care_assistant = db.StringProperty()
  planting_date = db.DateProperty()
  dbh = db.StringProperty()
  plot_size = db.StringProperty()
  permit_notes = db.StringProperty()
  geoloc = db.GeoPtProperty()
  geoboxes = db.StringListProperty()

  # List of resolutions and slices. Should be in increasing order of size/scope.
  GEOBOX_CONFIGS = ((4, 5, True),
                    (3, 2, True),
                    (3, 8, False),
                    (3, 16, False),
                    (2, 5, False))

  @classmethod
  def create(cls, **kwargs):
    """Build an SFTree instance suitable for db.put()"""
    kwargs['tree_id'] = int(kwargs['tree_id'])
    lat = kwargs.pop('latitude')
    lon = kwargs.pop('longitude')
    kwargs['geoloc'] = db.GeoPt(lat, lon)
    
    kwargs['geoboxes'] = cls.gen_geoboxes(lat, lon)

    kwargs['tree_order'] = int(kwargs['tree_order'])
    if kwargs['planting_date']:
      kwargs['planting_date'] = datetime.strptime(kwargs['planting_date'],
                                                  '%m/%d/%Y').date()
    else:
      kwargs['planting_date'] = None
      
    return cls(**kwargs)


  @classmethod
  def query(cls, lat, lon, max_results, min_params):
    """Find N number of trees around lat/lon.
    
    args:
      lat: float
      lon: float
      max_results: float
      min_params: 2-value tuple of ints
    """
    found_trees = {}
    for params in cls.GEOBOX_CONFIGS[:3]:
      if len(found_trees) >= max_results:
        break
      if params < min_params:
        break

      resolution, slice, unused = params
      box = geobox.compute(lat, lon, resolution, slice)
      logging.info("Searching for box=%s at resolution=%s, slice=%s",
                    box, resolution, slice)
      query = cls.all()
      query.filter("geoboxes =", box)
      #TODO: more filters
      results = query.fetch(100)
      logging.info("Found %d results", len(results))

      for result in results:
        if result.tree_id not in found_trees:
          found_trees[result.tree_id] = result

    trees_by_distance = []
    for tree in found_trees.itervalues():
      distance = _earth_distance(lat, lon, tree.geoloc.lat, tree.geoloc.lon)
      trees_by_distance.append((distance, tree))
    trees_by_distance.sort()

    return trees_by_distance[:max_results]
          
  @classmethod
  def gen_geoboxes(cls, lat, lon):
    """For a given latitude/longitude, return a list of relevant geoboxes.
    
    For more details on geoboxes, see geobox.py."""
    all_boxes = []
    for (resolution, slice, use_set) in cls.GEOBOX_CONFIGS:
      if use_set:
        all_boxes.extend(geobox.compute_set(lat, lon, resolution, slice))
      else:
        all_boxes.append(geobox.compute(lat, lon, resolution, slice))
    return all_boxes
  
  def update_geoboxes(self):
    self.geoboxes = self.gen_geoboxes(self.geoloc.lat, self.geoloc.lon)
  