#Juan Guajardo Gutierrez - 1002128662
#Ghiya El Daouk El Kadi - 1002165392

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
        # Get ITEM data
        cur.execute("SELECT * FROM ITEM")
        item_columns = [desc[0] for desc in cur.description]
        item_rows = cur.fetchall()
        item_list = [dict(zip(item_columns, row)) for row in item_rows]

        # Get VENDOR data
        cur.execute("SELECT * FROM VENDOR")
        vendor_columns = [desc[0] for desc in cur.description]
        vendor_rows = cur.fetchall()
        vendor_list = [dict(zip(vendor_columns, row)) for row in vendor_rows]

        # Get STORE_ITEM data
        cur.execute("SELECT * FROM STORE_ITEM")
        store_item_columns = [desc[0] for desc in cur.description]
        store_item_rows = cur.fetchall()
        store_item_list = [dict(zip(store_item_columns, row)) for row in store_item_rows]

        # Get VENDOR_STORE data
        cur.execute("SELECT * FROM VENDOR_STORE")
        vendor_store_columns = [desc[0] for desc in cur.description]
        vendor_store_rows = cur.fetchall()
        vendor_store_list = [dict(zip(vendor_store_columns, row)) for row in vendor_store_rows]

        # Get store inventory data
        cur.execute('''SELECT ITEM.iname AS "Item Name", ITEM.sprice AS "Price", STORE_ITEM.scount AS "Amount in Stock"
                    FROM STORE_ITEM JOIN ITEM ON STORE_ITEM.iid = ITEM.iid''')
        store_inventory_columns = [desc[0] for desc in cur.description]
        store_inventory_rows = cur.fetchall()
        store_inventory_list = [dict(zip(store_inventory_columns, row)) for row in store_inventory_rows]

        if not isinstance(item_list, list):
            item_list = []
        if not isinstance(vendor_list, list):
            vendor_list = []
        if not isinstance(store_item_list, list):
            store_item_list = []
        if not isinstance(vendor_store_list, list):
            vendor_store_list = []
        if not isinstance(store_inventory_list, list):
            store_inventory_list = []

        results = {
            "item_list": item_list,
            "vendor_list": vendor_list,
            "store_item_list": store_item_list,
            "vendor_store_list": vendor_store_list,
            "store_inventory_list": store_inventory_list
        }
    except Exception as e:
        results = {
            "error": str(e),
            "item_list": [],
            "vendor_list": [],
            "store_item_list": [],
            "vendor_store_list": [],
            "store_inventory_list": []
        }
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

@app.route("/link_vendor_item", methods=["POST"])
def link_vendor_item():
    vendor_id = request.form.get("vendor_id")
    item_id = request.form.get("item_id")
    item_count = request.form.get("item_count")
    cur = conn.cursor()
    
    try:
        # Verify the item and vendor exist
        cur.execute("SELECT vId FROM VENDOR WHERE vId = %s", (vendor_id,))
        if not cur.fetchone():
            return render_template("product_management.html", 
                                data={"error": "Vendor not found", 
                                     "item_list": [], 
                                     "vendor_list": []})
            
        cur.execute("SELECT iId FROM ITEM WHERE iId = %s", (item_id,))
        if not cur.fetchone():
            return render_template("product_management.html", 
                                data={"error": "Item not found", 
                                     "item_list": [], 
                                     "vendor_list": []})
        
        # Link the vendor to the store
        sql = "INSERT INTO VENDOR_STORE (vId, sId) VALUES (%s, 1)"
        cur.execute(sql, (vendor_id,))
        # Link the item to the store
        sql = "INSERT INTO STORE_ITEM (sId, iId, Scount) VALUES (1, %s, %s)"
        cur.execute(sql, (item_id, item_count))
        conn.commit()
        return redirect(url_for("home"))
        
    except Exception as e:
        conn.rollback()
        return render_template("product_management.html", 
                            data={"error": str(e), 
                                 "item_list": [], 
                                 "vendor_list": []})
    finally:
        cur.close()

@app.route("/delete_item", methods=["POST"])
def delete_item():
    item_id = request.form.get("item_id")
    cur = conn.cursor()
    # Delete the item and any vendor-item links
    try:
        # Can't directly delete the item because of referential integrity constraints
        cur.execute("BEGIN")
        # First delete the entry in STORE_ITEM
        cur.execute("DELETE FROM STORE_ITEM WHERE iid = %s", (item_id,))
        # Then delete the item itself
        cur.execute("DELETE FROM ITEM WHERE iid = %s", (item_id,))
        # Delete the entry in VENDOR_STORE
        cur.execute("DELETE FROM VENDOR_STORE WHERE vid = 201 AND sid = 1")
        # Finally, delete the vendor
        cur.execute("DELETE FROM VENDOR WHERE vid = 201")
        conn.commit()
        return redirect(url_for("home"))
        
    except Exception as e:
        conn.rollback()
        return render_template("product_management.html", 
                            data={"error": f"Error deleting item: {str(e)}", 
                                 "item_list": [], 
                                 "vendor_list": [],
                                 "store_item_list": [],
                                 "vendor_store_list": [],
                                 "store_inventory_list": []})
    finally:
        cur.close()

@app.route("/update_item_price", methods=["POST"])
def update_item_price():
    item_id = request.form.get("item_id")
    new_price = request.form.get("new_price")

    cur = conn.cursor()
    try:
        cur.execute("UPDATE ITEM SET sprice = %s WHERE iid = %s", (new_price, item_id,))
        conn.commit()
        return redirect(url_for("home"))
    except Exception as e:
        conn.rollback()
        return render_template("product_management.html", 
                            data={"error": f"Error updating item: {str(e)}", 
                                 "item_list": []})
    finally:
        cur.close()
if __name__ == "__main__":
    app.run(debug=True)

