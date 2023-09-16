"""
Make a geojson based on:
db path
Selected feedstock
Selected region type
Selected state
Consumer centers (display or not)
year
"""

import sqlite3
import json
import pandas as pd


def make_poly_features(db_path, feedstock_id, region_type, year, uf=None):
    if region_type not in ("mun", "imed", "inter", "uf"):
        raise ValueError ('region_type must be "mun", "imed", "inter" or "uf"')
    region_type = {"mun":"municipios", "imed": "imediatas", "inter": "intermediarias", "uf":"uf"}[region_type]

    con = sqlite3.connect(db_path)
    my_cursor = con.cursor()

    query = my_cursor.execute(
        f"""
        WITH prod_table AS(
            SELECT mun_id, quantity_produced
            FROM feedstock_production
            WHERE feedstock_id = ? AND year = ?
        ),

        prod_table_regions AS (
            SELECT
                {region_type}.id AS cod_ibge,
                {region_type}.name AS name,
                {region_type}.population AS population, 
                {region_type}.multi_polygon AS multi_polygon,
                {region_type}.geometry AS geometry,
                SUM(prod_table.quantity_produced) AS quantity_produced
            FROM prod_table
            INNER JOIN municipios ON municipios.id = prod_table.mun_id
            INNER JOIN imediatas ON imediatas.id = municipios.imed_id
            INNER JOIN intermediarias ON intermediarias.id = imediatas.inter_id
            INNER JOIN uf ON uf.id = intermediarias.uf_id
            WHERE uf.abbr = ? OR ? IS NULL
            GROUP BY {region_type}.id
        )
        
        SELECT * FROM prod_table_regions
        """,
        [feedstock_id, year, uf, uf]
    )

    poly_features = []
    for row in query:
        cod_ibge, name, population, multi_polygon, geometry, quantity_produced = row
        geometry = json.loads(geometry)

        if multi_polygon == 1:
            geometry_type = "MultiPolygon"
        else:
            geometry_type = "Polygon"

        feature = {"type": "Feature"}
        properties = {"id": cod_ibge, "name": name, "population": population, "quantity_produced": quantity_produced}
        feature["properties"] = properties
        feature["geometry"] = {"type": geometry_type, "coordinates": geometry}
        poly_features.append(
            feature
        )

    con.close()
    return poly_features

def make_point_features(db_path, product_id, uf=None):
    con = sqlite3.connect(db_path)
    my_cursor = con.cursor()

    query = my_cursor.execute(
        """
        WITH consumer_center_coords AS (
        SELECT
            municipios.centroid_lat AS centroid_lat,
            municipios.centroid_lon AS centroid_lon,
            consumer_center.demand AS demand,
            uf.abbr AS uf_abbr,
            consumer_center.mun_id AS mun_id
        FROM consumer_center
        INNER JOIN municipios ON consumer_center.mun_id = municipios.id
        INNER JOIN imediatas ON imediatas.id = municipios.imed_id
        INNER JOIN intermediarias ON intermediarias.id = imediatas.inter_id
        INNER JOIN uf ON uf.id = intermediarias.uf_id
        WHERE consumer_center.product_id = ? 
        )

        SELECT *
        FROM consumer_center_coords
        WHERE uf_abbr = ? OR ? IS NULL;
        """
        ,
        [product_id, uf, uf]
    )

    point_features = []
    for row in query:
        centroid_lat, centroid_lon, demand, uf_abbr, mun_id = row
        feature = {"type": "Feature"}
        feature["geometry"] = {"type": "Point", "coordinates": [centroid_lon, centroid_lat]}
        feature["properties"] = {"mun_id": mun_id, "demand": demand}
        point_features.append(feature)

    con.close()

    return point_features



def make_geojson(db_path, feedstock_id, region_type, year, product_id=None, uf=None, consumer_centers=True):
    poly_features = make_poly_features(db_path, feedstock_id, region_type, year, uf)
    if consumer_centers:
        features = poly_features + make_point_features(db_path, product_id, uf)
    else:
        features = poly_features

    return {"type":"FeatureCollection", "features": features}
