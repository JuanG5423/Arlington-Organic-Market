#Juan Guajardo Gutierrez - 1002128662
#Ghiya El Daouk El Kadi - 1002165392


from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
import pandas as pd

app = Flask(__name__)
CORS(app) 

conn = psycopg2.connect(
    host="localhost",
    database="Organic Market DB",
    user="postgres",
    password="1234"
)

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    sql = data.get('query')

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
        return jsonify(results)
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()

if __name__ == '__main__':
    app.run(debug=True)

