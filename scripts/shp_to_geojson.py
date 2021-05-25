'''
adapted from https://snorfalorpagus.net/blog/2017/02/19/sorted-open-data-part-2-with-d3/
'''

import fiona
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import transform
from functools import partial
import pyproj
import json


# reproject from OSGB to WGS84
# deprecated: need to update to pyproj.Transformer object
project = partial(
    pyproj.transform,
    pyproj.Proj("epsg:27700"),
    pyproj.Proj("epsg:4326"),
    always_xy=True)

# round coordinates
def round_coord(x, y, z=None):
    x = round(x, 5)
    y = round(y, 5)
    return tuple(filter(None, [x, y, z]))

# reduce a geometry
def minify(geometry):
    #geometry = geometry.simplify(1000)     # set to e.g. 25 for medium and 1000 for low-res
    geometry = transform(project, geometry)
    geometry = transform(round_coord, geometry)
    return geometry

features = []
with fiona.open("../shapefiles/DNO_License_Areas_20200506.shp") as src:
    for feature in src:
        geometry = shape(feature["geometry"])
        geometry = minify(geometry)
        feature["geometry"] = mapping(geometry)
        feature["properties"] = {
            "name": feature["properties"]["Name"],
            "long_name": feature["properties"]["LongName"],
            "shape_area": int(float(feature["properties"]["ID"]))
        }
        features.append(feature)

fc = {"type": "FeatureCollection", "features": features}

with open('../GeoJSON/DNO_max.json', 'w') as outfile:
    data = json.dump(fc, outfile)