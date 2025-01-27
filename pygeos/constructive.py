from enum import IntEnum
import numpy as np
from . import Geometry  # NOQA
from . import ufuncs


__all__ = [
    "BufferCapStyles",
    "BufferJoinStyles",
    "boundary",
    "buffer",
    "centroid",
    "convex_hull",
    "delaunay_triangles",
    "envelope",
    "extract_unique_points",
    "point_on_surface",
    "simplify",
    "snap",
    "voronoi_polygons",
]


class BufferCapStyles(IntEnum):
    ROUND = 1
    FLAT = 2
    SQUARE = 3


class BufferJoinStyles(IntEnum):
    ROUND = 1
    MITRE = 2
    BEVEL = 3


def boundary(geometry, **kwargs):
    """Returns the topological boundary of a geometry.

    Parameters
    ----------
    geometry : Geometry or array_like
        This function will raise for non-empty geometrycollections.

    Examples
    --------
    >>> boundary(Geometry("POINT (0 0)"))
    <pygeos.Geometry GEOMETRYCOLLECTION EMPTY>
    >>> boundary(Geometry("LINESTRING(0 0, 1 1, 1 2)"))
    <pygeos.Geometry MULTIPOINT (0 0, 1 2)>
    >>> boundary(Geometry("LINEARRING (0 0, 1 0, 1 1, 0 1, 0 0)"))
    <pygeos.Geometry MULTIPOINT EMPTY>
    >>> boundary(Geometry("POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"))
    <pygeos.Geometry LINESTRING (0 0, 1 0, 1 1, 0 1, 0 0)>
    >>> boundary(Geometry("MULTIPOINT (0 0, 1 2)")) is None
    True
    """
    return ufuncs.boundary(geometry, **kwargs)


def buffer(
    geometry,
    radius,
    quadsegs=8,
    cap_style="round",
    join_style="round",
    mitre_limit=5.0,
    single_sided=False,
    **kwargs
):
    """
    Computes the buffer of a geometry for positive and negative buffer radius.

    The buffer of a geometry is defined as the Minkowski sum (or difference,
    for negative width) of the geometry with a circle with radius equal to the
    absolute value of the buffer radius.

    The buffer operation always returns a polygonal result. The negative
    or zero-distance buffer of lines and points is always empty.

    Parameters
    ----------
    geometry : Geometry or array_like
    width : float or array_like
        Specifies the circle radius in the Minkowski sum (or difference).
    quadsegs : int
        Specifies the number of linear segments in a quarter circle in the
        approximation of circular arcs.
    cap_style : {'round', 'square', 'flat'}
        Specifies the shape of buffered line endings. 'round' results in
        circular line endings (see ``quadsegs``). Both 'square' and 'flat'
        result in rectangular line endings, only 'flat' will end at the
        original vertex, while 'square' involves adding the buffer width.
    join_style : {'round', 'bevel', 'sharp'}
        Specifies the shape of buffered line midpoints. 'round' results in
        rounded shapes. 'bevel' results in a beveled edge that touches the
        original vertex. 'mitre' results in a single vertex that is beveled
        depending on the ``mitre_limit`` parameter.
    mitre_limit : float
        Crops of 'mitre'-style joins if the point is displaced from the
        buffered vertex by more than this limit.
    single_sided : bool
        Only buffer at one side of the geometry.

    Examples
    --------
    >>> buffer(Geometry("POINT (10 10)"), 2, quadsegs=1)
    <pygeos.Geometry POLYGON ((12 10, 10 8, 8 10, 10 12, 12 10))>
    >>> buffer(Geometry("POINT (10 10)"), 2, quadsegs=2)
    <pygeos.Geometry POLYGON ((12 10, 11.4 8.59, 10 8, 8.59 8.59, 8 10, 8.59 11.4, 10 12, 11.4 11.4, 12 10))>
    >>> buffer(Geometry("POINT (10 10)"), -2, quadsegs=1)
    <pygeos.Geometry POLYGON EMPTY>
    >>> line = Geometry("LINESTRING (10 10, 20 10)")
    >>> buffer(line, 2, cap_style="square")
    <pygeos.Geometry POLYGON ((20 12, 22 12, 22 8, 10 8, 8 8, 8 12, 20 12))>
    >>> buffer(line, 2, cap_style="flat")
    <pygeos.Geometry POLYGON ((20 12, 20 8, 10 8, 10 12, 20 12))>
    >>> buffer(line, 2, single_sided=True, cap_style="flat")
    <pygeos.Geometry POLYGON ((20 10, 10 10, 10 12, 20 12, 20 10))>
    >>> line2 = Geometry("LINESTRING (10 10, 20 10, 20 20)")
    >>> buffer(line2, 2, cap_style="flat", join_style="bevel")
    <pygeos.Geometry POLYGON ((18 12, 18 20, 22 20, 22 10, 20 8, 10 8, 10 12, 18 12))>
    >>> buffer(line2, 2, cap_style="flat", join_style="mitre")
    <pygeos.Geometry POLYGON ((18 12, 18 20, 22 20, 22 8, 10 8, 10 12, 18 12))>
    >>> buffer(line2, 2, cap_style="flat", join_style="mitre", mitre_limit=1)
    <pygeos.Geometry POLYGON ((18 12, 18 20, 22 20, 21.8 9, 21 8.17, 10 8, 10 12, 18 12))>
    >>> square = Geometry("POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")
    >>> buffer(square, 2, join_style="mitre")
    <pygeos.Geometry POLYGON ((-2 -2, -2 12, 12 12, 12 -2, -2 -2))>
    >>> buffer(square, -2, join_style="mitre")
    <pygeos.Geometry POLYGON ((2 2, 2 8, 8 8, 8 2, 2 2))>
    >>> buffer(square, -5, join_style="mitre")
    <pygeos.Geometry POLYGON EMPTY>
    >>> buffer(line, float("nan")) is None
    True
    """
    if isinstance(cap_style, str):
        cap_style = BufferCapStyles[cap_style.upper()].value
    if isinstance(join_style, str):
        join_style = BufferJoinStyles[join_style.upper()].value
    if not np.isscalar(quadsegs):
        raise TypeError("quadsegs only accepts scalar values")
    if not np.isscalar(cap_style):
        raise TypeError("cap_style only accepts scalar values")
    if not np.isscalar(join_style):
        raise TypeError("join_style only accepts scalar values")
    if not np.isscalar(mitre_limit):
        raise TypeError("mitre_limit only accepts scalar values")
    if not np.isscalar(single_sided):
        raise TypeError("single_sided only accepts scalar values")
    return ufuncs.buffer(
        geometry,
        radius,
        np.intc(quadsegs),
        np.intc(cap_style),
        np.intc(join_style),
        mitre_limit,
        np.bool(single_sided),
        **kwargs
    )


def centroid(geometry, **kwargs):
    """Computes the geometric center (center-of-mass) of a geometry.

    For multipoints this is computed as the mean of the input coordinates.
    For multilinestrings the centroid is weighted by the length of each
    line segment. For multipolygons the centroid is weighted by the area of
    each polygon.

    Parameters
    ----------
    geometry : Geometry or array_like

    Examples
    --------
    >>> centroid(Geometry("POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))"))
    <pygeos.Geometry POINT (5 5)>
    >>> centroid(Geometry("LINESTRING (0 0, 2 2, 10 10)"))
    <pygeos.Geometry POINT (5 5)>
    >>> centroid(Geometry("MULTIPOINT (0 0, 10 10)"))
    <pygeos.Geometry POINT (5 5)>
    """
    return ufuncs.centroid(geometry, **kwargs)


def convex_hull(geometry, **kwargs):
    """Computes the minimum convex geometry that encloses an input geometry.

    Parameters
    ----------
    geometry : Geometry or array_like

    Examples
    --------
    >>> convex_hull(Geometry("MULTIPOINT (0 0, 10 0, 10 10)"))
    <pygeos.Geometry POLYGON ((0 0, 10 10, 10 0, 0 0))>
    >>> convex_hull(Geometry("POLYGON EMPTY"))
    <pygeos.Geometry GEOMETRYCOLLECTION EMPTY>
    """
    return ufuncs.convex_hull(geometry, **kwargs)


def delaunay_triangles(geometry, tolerance=0.0, only_edges=False, **kwargs):
    """Computes a Delaunay triangulation around the vertices of an input
    geometry.

    The output is a geometrycollection containing polygons (default)
    or linestrings (see only_edges). Returns an None if an input geometry
    contains less than 3 vertices.

    Parameters
    ----------
    geometry : Geometry or array_like
    tolerance : float or array_like
        Snap input vertices together if their distance is less than this value.
    only_edges : bool or array_like
        If set to True, the triangulation will return a collection of
        linestrings instead of polygons.

    Examples
    --------
    >>> points = Geometry("MULTIPOINT (50 30, 60 30, 100 100)")
    >>> delaunay_triangles(points)
    <pygeos.Geometry GEOMETRYCOLLECTION (POLYGON ((50 30, 60 30, 100 100, 50 30)))>
    >>> delaunay_triangles(points, only_edges=True)
    <pygeos.Geometry MULTILINESTRING ((50 30, 100 100), (50 30, 60 30), (60 30, 100 100))>
    >>> delaunay_triangles(Geometry("MULTIPOINT (50 30, 51 30, 60 30, 100 100)"), tolerance=2)
    <pygeos.Geometry GEOMETRYCOLLECTION (POLYGON ((50 30, 60 30, 100 100, 50 30)))>
    >>> delaunay_triangles(Geometry("POLYGON ((50 30, 60 30, 100 100, 50 30))"))
    <pygeos.Geometry GEOMETRYCOLLECTION (POLYGON ((50 30, 60 30, 100 100, 50 30)))>
    >>> delaunay_triangles(Geometry("LINESTRING (50 30, 60 30, 100 100)"))
    <pygeos.Geometry GEOMETRYCOLLECTION (POLYGON ((50 30, 60 30, 100 100, 50 30)))>
    >>> delaunay_triangles(Geometry("GEOMETRYCOLLECTION EMPTY"))
    <pygeos.Geometry GEOMETRYCOLLECTION EMPTY>
    """
    return ufuncs.delaunay_triangles(geometry, tolerance, only_edges, **kwargs)


def envelope(geometry, **kwargs):
    """Computes the minimum bounding box that encloses an input geometry.

    Parameters
    ----------
    geometry : Geometry or array_like

    Examples
    --------
    >>> envelope(Geometry("LINESTRING (0 0, 10 10)"))
    <pygeos.Geometry POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))>
    >>> envelope(Geometry("MULTIPOINT (0 0, 10 0, 10 10)"))
    <pygeos.Geometry POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))>
    >>> envelope(Geometry("POINT (0 0)"))
    <pygeos.Geometry POINT (0 0)>
    >>> envelope(Geometry("GEOMETRYCOLLECTION EMPTY"))
    <pygeos.Geometry POINT EMPTY>
    """
    return ufuncs.envelope(geometry, **kwargs)


def extract_unique_points(geometry, **kwargs):
    """Returns all distinct vertices of an input geometry as a multipoint.

    Note that only 2 dimensions of the vertices are considered when testing
    for equality.

    Parameters
    ----------
    geometry : Geometry or array_like

    Examples
    --------
    >>> extract_unique_points(Geometry("POINT (0 0)"))
    <pygeos.Geometry MULTIPOINT (0 0)>
    >>> extract_unique_points(Geometry("LINESTRING(0 0, 1 1, 1 1)"))
    <pygeos.Geometry MULTIPOINT (0 0, 1 1)>
    >>> extract_unique_points(Geometry("POLYGON((0 0, 1 0, 1 1, 0 0))"))
    <pygeos.Geometry MULTIPOINT (0 0, 1 0, 1 1)>
    >>> extract_unique_points(Geometry("MULTIPOINT (0 0, 1 1, 0 0)"))
    <pygeos.Geometry MULTIPOINT (0 0, 1 1)>
    >>> extract_unique_points(Geometry("LINESTRING EMPTY"))
    <pygeos.Geometry MULTIPOINT EMPTY>
    """
    return ufuncs.extract_unique_points(geometry, **kwargs)


def point_on_surface(geometry, **kwargs):
    """Returns a point that intersects an input geometry.

    Parameters
    ----------
    geometry : Geometry or array_like

    Examples
    --------
    >>> point_on_surface(Geometry("POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))"))
    <pygeos.Geometry POINT (5 5)>
    >>> point_on_surface(Geometry("LINESTRING (0 0, 2 2, 10 10)"))
    <pygeos.Geometry POINT (2 2)>
    >>> point_on_surface(Geometry("MULTIPOINT (0 0, 10 10)"))
    <pygeos.Geometry POINT (0 0)>
    >>> point_on_surface(Geometry("POLYGON EMPTY"))
    <pygeos.Geometry POINT EMPTY>
    """
    return ufuncs.point_on_surface(geometry, **kwargs)


def simplify(geometry, tolerance, preserve_topology=False, **kwargs):
    """Returns a simplified version of an input geometry using the
    Douglas-Peucker algorithm.

    Parameters
    ----------
    geometry : Geometry or array_like
    tolerance : float or array_like
        The maximum allowed geometry displacement. The higher this value, the
        smaller the number of vertices in the resulting geometry.
    preserve_topology : bool
        If set to True, the operation will avoid creating invalid geometries.

    Examples
    --------
    >>> line = Geometry("LINESTRING (0 0, 1 10, 0 20)")
    >>> simplify(line, tolerance=0.9)
    <pygeos.Geometry LINESTRING (0 0, 1 10, 0 20)>
    >>> simplify(line, tolerance=1)
    <pygeos.Geometry LINESTRING (0 0, 0 20)>
    >>> polygon_with_hole = Geometry("POLYGON((0 0, 0 10, 10 10, 10 0, 0 0), (2 2, 2 4, 4 4, 4 2, 2 2))")
    >>> simplify(polygon_with_hole, tolerance=4, preserve_topology=True)
    <pygeos.Geometry POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0), (2 2, 2 4, 4 4, 4 2, 2 2))>
    >>> simplify(polygon_with_hole, tolerance=4, preserve_topology=False)
    <pygeos.Geometry POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))>
    """
    if preserve_topology:
        return ufuncs.simplify_preserve_topology(geometry, tolerance, **kwargs)
    else:
        return ufuncs.simplify(geometry, tolerance, **kwargs)


def snap(geometry, reference, tolerance, **kwargs):
    """Snaps an input geometry to reference geometry's vertices.

    The tolerance is used to control where snapping is performed.
    The result geometry is the input geometry with the vertices snapped.
    If no snapping occurs then the input geometry is returned unchanged.

    Parameters
    ----------
    geometry : Geometry or array_like
    reference : Geometry or array_like
    tolerance : float or array_like

    Examples
    --------
    >>> point = Geometry("POINT (0 2)")
    >>> snap(Geometry("POINT (0.5 2.5)"), point, tolerance=1)
    <pygeos.Geometry POINT (0 2)>
    >>> snap(Geometry("POINT (0.5 2.5)"), point, tolerance=0.49)
    <pygeos.Geometry POINT (0.5 2.5)>
    >>> polygon = Geometry("POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))")
    >>> snap(polygon, Geometry("POINT (8 10)"), tolerance=5)
    <pygeos.Geometry POLYGON ((0 0, 0 10, 8 10, 10 0, 0 0))>
    >>> snap(polygon, Geometry("LINESTRING (8 10, 8 0)"), tolerance=5)
    <pygeos.Geometry POLYGON ((0 0, 0 10, 8 10, 8 0, 0 0))>
    """
    return ufuncs.snap(geometry, reference, tolerance, **kwargs)


def voronoi_polygons(
    geometry, tolerance=0.0, extend_to=None, only_edges=False, **kwargs
):
    """Computes a Voronoi diagram from the vertices of an input geometry.

    The output is a geometrycollection containing polygons (default)
    or linestrings (see only_edges). Returns empty if an input geometry
    contains less than 2 vertices or if the provided extent has zero area.

    Parameters
    ----------
    geometry : Geometry or array_like
    tolerance : float or array_like
        Snap input vertices together if their distance is less than this value.
    extend_to : Geometry or array_like
        If provided, the diagram will be extended to cover the envelope of this
        geometry (unless this envelope is smaller than the input geometry).
    only_edges : bool or array_like
        If set to True, the triangulation will return a collection of
        linestrings instead of polygons.

    Examples
    --------
    >>> points = Geometry("MULTIPOINT (2 2, 4 2)")
    >>> voronoi_polygons(points)
    <pygeos.Geometry GEOMETRYCOLLECTION (POLYGON ((3 0, 0 0, 0 4, 3 4, 3 0)), POLYGON ((3 4, 6 4, 6 0, 3 0, 3 4)))>
    >>> voronoi_polygons(points, only_edges=True)
    <pygeos.Geometry LINESTRING (3 4, 3 0)>
    >>> voronoi_polygons(Geometry("MULTIPOINT (2 2, 4 2, 4.2 2)"), 0.5, only_edges=True)
    <pygeos.Geometry LINESTRING (3 4.2, 3 -0.2)>
    >>> voronoi_polygons(points, extend_to=Geometry("LINESTRING (0 0, 10 10)"), only_edges=True)
    <pygeos.Geometry LINESTRING (3 10, 3 0)>
    >>> voronoi_polygons(Geometry("LINESTRING (2 2, 4 2)"), only_edges=True)
    <pygeos.Geometry LINESTRING (3 4, 3 0)>
    >>> voronoi_polygons(Geometry("POINT (2 2)"))
    <pygeos.Geometry GEOMETRYCOLLECTION EMPTY>
    """
    return ufuncs.voronoi_polygons(geometry, tolerance, extend_to, only_edges, **kwargs)
