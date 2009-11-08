#!/usr/bin/env python
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

"""Convert SPCS83 coords in San Francisco's Tree data to Lat/Lon

The city of San Francisco published a spreadsheet of trees at
http://datasf.org . The X/Y coordinates lie within SPCS California 
Zone 3.

Helpful description of SPCS, Planar to Elipsoid coversions and the
Lambert Cone Projection,
http://www.ngs.noaa.gov/PUBS_LIB/ManualNOSNGS5.pdf

The original spreadsheet is in Excel format, which I converted to CSV
using NeoOffice. The input for this script is CSV, quotechar=".""" 

__author__ = "Bradley Heilbrun <nurblieh@gmail.com>"

import csv, math, sys

# As defined by the US Survey Foot.
# http://en.wikipedia.org/wiki/Foot_(length)
METER_LENGTH = 39.37 # inches

# California uses Lambert Conical Projections. 
ccs_zone3 = { "Bs": 37.06666666666667, # southern parallel
              "Bn": 38.43333333333333, # northern parallel
              "Bb": 36.5,              # lat of grid origin
              "Lo": 120.5,             # central meridian
              "Nb": 500000.0000,       # Northing value @ Lo
              "Eo": 2000000.0000,      # Easting value @ Lo
              # Derived values
              "Bo":37.7510694363,
              "SinBo":math.sin(math.radians(37.7510694363)),
              "Rb":8385775.1723,
              "Ro":8246930.3684,
              "No":638844.8039,

              "G1": 9.010315015e-06,
              "G2": -6.90503e-15,
              "G3": -3.71614e-20,
              "G4": -9.8819e-28,
              }

def ft_to_m(ft):
  return (ft * 12) / METER_LENGTH

def spcs_to_latlong(N, E):
  """Covert SPCS planar coordinates to Elipsoidal lat/lon
  
  args:
    N: Northing in meters
    E: Easting in meters
  """
  Npr = N - ccs_zone3["No"]
  Epr = E - ccs_zone3["Eo"]
  Rpr = ccs_zone3["Ro"] - Npr
  Gamma = math.atan2(Epr, Rpr)
  longitude = ccs_zone3["Lo"] - (math.degrees(Gamma) / ccs_zone3["SinBo"])
  u = Npr - Epr * math.tan(Gamma / 2)
  del_phi = u * (ccs_zone3["G1"] +
           u * (ccs_zone3["G2"] +
           u * (ccs_zone3["G3"] + ccs_zone3["G4"] * u)))
           
  latitude = ccs_zone3["Bo"] + del_phi
  
  return latitude, longitude


def main():
  if len(sys.argv) < 3:
    print "Need 2 arguments."
    print "%s <in file> <out file>" % sys.argv[0]
    sys.exit(1)

  csv_file_orig = sys.argv[1]
  csv_file_geo = sys.argv[2]
  reader = csv.reader(open(csv_file_orig))
  writer = csv.writer(open(csv_file_geo, 'w'))
  # format: |TreeID|,|Legal Status|,|Species|,|Address|,|Tree Order at address|,|Site type|,|Plant type|,|Caretaker|,|Care Assistant|,|PlantingDate|,|DBH|,|PlotSize|,|Permit Notes|,|Xcoord|,|Ycoord|
  for tree in reader:
    # Only write trees for which we have a valid set of coords.
    try:
      n_ft, e_ft = float(tree[14]), float(tree[13])
    except ValueError:
      #writer.writerow(tree)
      continue
    n_m = ft_to_m(n_ft)
    e_m = ft_to_m(e_ft)
    latitude, longitude = spcs_to_latlong(n_m, e_m)
    tree[14] = latitude
    tree[13] = longitude * -1 # west
    writer.writerow(tree)

if __name__ == "__main__":
  main()
