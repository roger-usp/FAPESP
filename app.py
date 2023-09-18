from flask import Flask, render_template, jsonify
from geojson.geojson_maker import make_geojson
import sqlite3


db_path = "banco_de_dados/FAPESP.db"

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/feedstock_types")
def feedstock_types():
    con = sqlite3.connect(db_path)
    my_cursor = con.cursor()
    data = my_cursor.execute("SELECT id, name FROM feedstock_type;").fetchall()
    id_list, feedstock_type_list = zip(*data)
    data = {"feedstock_type_id": list(id_list), "feedstock_type": list(feedstock_type_list)}
    con.close()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)