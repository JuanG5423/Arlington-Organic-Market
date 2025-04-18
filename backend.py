from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2

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
        return render_template("index.html", result=results, cols=list(results[0].keys()))
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()

if __name__ == '__main__':
    app.run(debug=True)

