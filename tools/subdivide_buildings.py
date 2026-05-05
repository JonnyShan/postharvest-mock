#!/usr/bin/env python3
"""Subdivide OSM building polygons along their long axis into N bays.

For each site (lat, lng, room_count, label):
  1. Query Overpass for buildings within radius.
  2. Pick the biggest by polygon area (shoelace).
  3. Compute PCA primary axis (long direction).
  4. Project polygon onto primary axis, get extent.
  5. Sample N evenly-spaced bay centers along long axis.
  6. Snap each to point-in-polygon if outside (nudge to centroid).
  7. Print as JS coord array per site.
"""
import json
import math
import urllib.request
import urllib.parse
import urllib.error
import time

OVERPASS = "https://overpass-api.de/api/interpreter"

SITES = [
    # (label, lat, lng, room_count, radius_m)
    ("rockit-whakatu",       -39.6068,   176.8893,  12, 300),
    ("trucape-ceres",        -33.3742,    19.3082,   6, 400),
    ("calypso-bowen",        -20.0220,   148.2240,   3, 400),
    ("costa-mildura",        -34.2660,   142.2030,   2, 500),
    ("costa-corindi",        -30.0418,   153.1850,   1, 400),
    ("costa-walkamin",       -17.1311,   145.4378,   2, 400),
    ("driscolls-watsonville", 36.9220,  -121.7714,   5, 500),
    ("driscolls-oxnard",      34.2010,  -119.1766,   3, 500),
]

def overpass_buildings(lat, lng, radius):
    q = f'[out:json][timeout:30];(way["building"](around:{radius},{lat},{lng}););out geom;'
    data = urllib.parse.urlencode({"data": q}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                OVERPASS, data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": "postharvest-mock/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            print(f"  retry {attempt+1}: {e}")
            time.sleep(2 ** attempt)
    raise RuntimeError("Overpass failed")

def shoelace_area(coords):
    """Polygon area in (lat, lng) degree units (signed)."""
    n = len(coords)
    if n < 3: return 0.0
    s = 0.0
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        s += (x1 * y2) - (x2 * y1)
    return abs(s) / 2.0

def pick_biggest(elements):
    best = None
    best_area = 0.0
    for el in elements:
        if el.get("type") != "way": continue
        g = el.get("geometry", [])
        if len(g) < 3: continue
        coords = [(p["lat"], p["lon"]) for p in g]
        a = shoelace_area(coords)
        if a > best_area:
            best_area = a
            best = (el["id"], coords)
    return best

def to_meters(coords, lat0):
    """Convert (lat, lng) to local meter offsets centered at (lat0, lng0)."""
    lng0 = sum(c[1] for c in coords) / len(coords)
    cos_lat = math.cos(math.radians(lat0))
    return [(((c[1] - lng0) * cos_lat * 111111.0),
             ((c[0] - lat0)         * 111111.0)) for c in coords], lng0

def from_meters(x_m, y_m, lat0, lng0):
    cos_lat = math.cos(math.radians(lat0))
    return (lat0 + y_m / 111111.0,
            lng0 + x_m / (cos_lat * 111111.0))

def primary_axis(points_m):
    """Return unit vector along principal axis (in meters frame)."""
    n = len(points_m)
    cx = sum(p[0] for p in points_m) / n
    cy = sum(p[1] for p in points_m) / n
    sxx = syy = sxy = 0.0
    for x, y in points_m:
        dx = x - cx; dy = y - cy
        sxx += dx * dx; syy += dy * dy; sxy += dx * dy
    # Eigenvector for largest eigenvalue of [[sxx, sxy], [sxy, syy]]
    a = sxx; c = syy; b = sxy
    half = (a + c) / 2.0
    diff = (a - c) / 2.0
    rad = math.sqrt(diff * diff + b * b)
    lam = half + rad
    # Eigenvector: (b, lam - a) — fallback if b == 0
    vx = b
    vy = lam - a
    if abs(vx) < 1e-9 and abs(vy) < 1e-9:
        vx, vy = (1.0, 0.0) if a >= c else (0.0, 1.0)
    norm = math.hypot(vx, vy) or 1.0
    return cx, cy, (vx / norm, vy / norm)

def point_in_poly(x, y, poly):
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside

def subdivide(coords, n):
    if n <= 0: return []
    lat0 = sum(c[0] for c in coords) / len(coords)
    pts_m, lng0 = to_meters(coords, lat0)
    cx, cy, axis = primary_axis(pts_m)
    perp = (-axis[1], axis[0])
    # Project each polygon vertex onto axis
    projs = [(p[0] - cx) * axis[0] + (p[1] - cy) * axis[1] for p in pts_m]
    perp_projs = [(p[0] - cx) * perp[0] + (p[1] - cy) * perp[1] for p in pts_m]
    proj_min, proj_max = min(projs), max(projs)
    pp_min, pp_max = min(perp_projs), max(perp_projs)
    pp_mid = (pp_min + pp_max) / 2
    # Inset 5% from ends to keep pins safely inside
    span = proj_max - proj_min
    proj_min += span * 0.05
    proj_max -= span * 0.05
    out = []
    for i in range(n):
        t = (i + 0.5) / n
        p = proj_min + t * (proj_max - proj_min)
        x_m = cx + axis[0] * p + perp[0] * pp_mid
        y_m = cy + axis[1] * p + perp[1] * pp_mid
        # Verify inside polygon — if not, walk toward centroid
        for step in range(8):
            if point_in_poly(x_m, y_m, pts_m):
                break
            x_m = (x_m + cx) / 2
            y_m = (y_m + cy) / 2
        lat, lng = from_meters(x_m, y_m, lat0, lng0)
        out.append((lat, lng))
    return out

def main():
    results = {}
    for label, lat, lng, n_rooms, radius in SITES:
        print(f"\n=== {label} ({n_rooms} rooms) ===")
        try:
            data = overpass_buildings(lat, lng, radius)
        except Exception as e:
            print(f"  OVERPASS FAILED: {e}")
            results[label] = None
            continue
        elements = data.get("elements", [])
        print(f"  {len(elements)} buildings within {radius}m")
        big = pick_biggest(elements)
        if not big:
            print(f"  NO BUILDING FOUND")
            results[label] = None
            continue
        bid, coords = big
        print(f"  picked way {bid} with {len(coords)} vertices")
        rooms = subdivide(coords, n_rooms)
        print(f"  generated {len(rooms)} room coords")
        for i, (la, lo) in enumerate(rooms):
            print(f"    Room {i+1}: ({la:.6f}, {lo:.6f})")
        results[label] = {"way_id": bid, "rooms": rooms}
        time.sleep(1)  # rate-limit Overpass
    print("\n\n=== JS OUTPUT ===")
    print("const SITE_COORDS = " + json.dumps(
        {k: ([{"lat": r[0], "lng": r[1]} for r in v["rooms"]] if v else None) for k, v in results.items()},
        indent=2
    ) + ";")

if __name__ == "__main__":
    main()
