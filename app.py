from flask import Flask, render_template, jsonify
import sqlite3
from geojson.geojson_maker import make_poly_features


db_path = "banco_de_dados/FAPESP.db"

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/feedstocks")
def get_feedstocks():
    con = sqlite3.connect(db_path)
    my_cursor = con.cursor()
    data = my_cursor.execute(
        """
        SELECT DISTINCT feedstock_production.feedstock_id, feedstock.name
        FROM feedstock_production
        INNER JOIN feedstock ON feedstock_production.feedstock_id = feedstock.id
        """
    )
    data = data.fetchall()
    data = list(zip(*data))
    con.close()
    return jsonify({"feedstock_id": list(data[0]), "feedstock_name": list(data[1])})


@app.route("/years/<feedstock_id>")
def get_years(feedstock_id):
    con = sqlite3.connect(db_path)
    my_cursor = con.cursor()

    data = my_cursor.execute(
        """
        SELECT DISTINCT year
        FROM feedstock_production
        WHERE feedstock_id = ?;
        """,
        feedstock_id
    )
    data = data.fetchall()
    data = list(zip(*data))[0]

    con.close()
    return jsonify(data)


@app.route("/geojson/<feedstock_id>/<region_type>/<year>")
def geojson(feedstock_id, region_type, year):
    features = make_poly_features(db_path, feedstock_id, region_type, year)
    return jsonify({"type":"FeatureCollection", "features": features})

if __name__ == "__main__":
    app.run(debug=True)