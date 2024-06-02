import sys
from io import StringIO
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas
import scipy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///code_runs.db'
db = SQLAlchemy(app)
CORS(app, resources={r"/run_code": {"origins": "*"}, r"/get_latest_code": {"origins": "*"}, r"/submit_code": {"origins": "*"}})

@app.before_request
def create_tables():
    # The following line will remove this handler, making it
    # only run on the first request
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()

class CodeRun(db.Model):
    __tablename__ = 'code_run'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    result = db.Column(db.String, nullable=False)

@app.route('/submit_code', methods=['POST'])
def submit_code():
    code = request.json.get('code')
    # Redirect stdout
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    try:
        exec(code)
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        latest_run = CodeRun.query.first()
        if latest_run:
            latest_run.code = code
            latest_run.result = output
        else:
            new_run = CodeRun(code=code, result=output)
            db.session.add(new_run)
        db.session.commit()
        return jsonify({"result": output}), 200
    except Exception as e:
        sys.stdout = old_stdout
        return jsonify({"error": str(e)}), 400

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code')
    # Redirect stdout
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    try:
        exec(code)
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        return jsonify({"result": output}), 200
    except Exception as e:
        sys.stdout = old_stdout
        return jsonify({"error": str(e)}), 400

@app.route('/get_latest_code', methods=['GET'])
def get_latest_code():
    latest_run = CodeRun.query.first()
    if latest_run:
        return jsonify({"latest_code": latest_run.code, "latest_result": latest_run.result}), 200
    else:
        return jsonify({"error": "No code available"}), 404


if __name__ == '__main__':
    app.run(debug=True)
