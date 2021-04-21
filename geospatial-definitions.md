This file contains some definitions, key knowledge that I have learned.

crs: Coordinate Reference System
```
Specifies the space that the coordinates are in.
```

epsg: European Petroleum Survey Group
```
They produce a database of coordinate system information.
EPSG:4326 is a coordinate system for traditional lat/long coordinates.
```

GeoJSON:
```
A method of storing and representing geospatial data.
A long/lat order is required when a GeoJSON is created.
There are a variety of issues with GeoJSON including the 180th Meridian problem.
The problem describes how geometries that cross the 180th Meridian may not be represented as intended.
```

TopoJSON:
```
An extension of GeoJSON that encodes topological features. 
Uses sequences of Arcs and Points to define geometry.
```

Uber H3:
```
Uber H3 is a spatial indexing system, and has a variety of bindings in different languages.
The library runs off of H3Cells, and H3Index objects.
```
