from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import psycopg2
import pandas as pd
import json

app = Flask(__name__)
CORS(app) 


conn = psycopg2.connect(
    host="localhost",
    database="Organic Market DB",
    user="postgres",
    password="1234"
)

@app.route("/")
def home():
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM ITEM")
        item_columns = [desc[0] for desc in cur.description]
        item_rows = cur.fetchall()
        item_list = [dict(zip(item_columns, row)) for row in item_rows]

        cur.execute("SELECT * FROM VENDOR")
        vendor_columns = [desc[0] for desc in cur.description]
        vendor_rows = cur.fetchall()
        vendor_list = [dict(zip(vendor_columns, row)) for row in vendor_rows]

        if not isinstance(item_list, list):
            item_list = []
        if not isinstance(vendor_list, list):
            vendor_list = []

        results = {"item_list": item_list, "vendor_list": vendor_list}
    except Exception as e:
        results = {"error": str(e), "item_list": [], "vendor_list": []}
    finally:
        cur.close()
    return render_template("product_management.html", data=results)

@app.route("/index.html")
def index():
    data = request.args.get("data")
    parsed_data = None

    if data:
        try:
            parsed_data = json.loads(data)
        except Exception as e:
            parsed_data = {"error": f"Failed to parse data: {str(e)}"}
    print(parsed_data)
    return render_template("index.html", data=parsed_data)


@app.route("/query", methods=["POST"])
def query():
    sql = request.form.get("query")

    cur = conn.cursor()
    try:
        cur.execute(sql)
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
        else:
            results = {"message": "Query executed successfully."}
        conn.commit()
        data = json.dumps(results)
        return redirect(url_for("index", data=json.dumps(results)))
    except Exception as e:
        conn.rollback()
        print("Error")
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
    
@app.route("/add_product", methods=["POST"])
def add_product():
    id = request.form.get("product_id")
    name = request.form.get("product_name")
    cost = request.form.get("product_cost")
    category = request.form.get("product_category")
    cur = conn.cursor()
    try:
        sql = "INSERT INTO ITEM (iid, iname, sprice, category) VALUES (%s, %s, %s, %s) "
        cur.execute(sql, (id, name, cost, category))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return render_template("product_management.html", data={"error":str(e)})
    finally:
        cur.close()
    return redirect(url_for("home"))

@app.route("/add_vendor", methods=["POST"])
def add_vendor():
    id = request.form.get("vendor_id")
    name = request.form.get("vendor_name")
    street = request.form.get("vendor_street")
    city = request.form.get("vendor_city")
    state = request.form.get("vendor_state")
    zipcode = request.form.get("vendor_zip")
    cur = conn.cursor()
    try:
        sql = "INSERT INTO VENDOR (vid, vname, street, city, stateab, zipcode) VALUES (%s, %s, %s, %s, %s, %s) "
        cur.execute(sql, (id, name, street, city, state, zipcode))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return render_template("product_management.html", data={"error":str(e)})
    finally:
        cur.close()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

