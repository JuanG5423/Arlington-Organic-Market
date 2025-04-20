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

@app.route('/')
def index():
    data = request.args.get('data')
    parsed_data = None

    if data:
        try:
            parsed_data = json.loads(data)
        except Exception as e:
            parsed_data = {"error": f"Failed to parse data: {str(e)}"}
    print(parsed_data)
    #return render_template('index.html', data=parsed_data)
    return render_template("product_management.html")


@app.route('/query', methods=['POST'])
def query():
    sql = request.form.get('query')

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
        print('Error')
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()

if __name__ == '__main__':
    app.run(debug=True)

