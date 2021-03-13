
from flask import Flask, request
from db_model import Employee
import json

app = Flask(__name__)


@app.route('/Employee', methods=['GET', 'POST'])
def fnEmployee():
    if request.method == 'GET':
        # select
        q = Employee.select()
        for k in request.args:
            # filter
            field = getattr(Employee, k)
            q = q.where(field == request.args[k])
        return json.dumps(list(q.dicts()))
    elif request.method == 'POST':
        if 'id' in request.form:
            # update
            q = Employee.update(request.form).where(Employee.id == request.form['id'])
            print(q.sql())
            q.execute()
            return f'updated ' + request.form['id'] 
        else:
            # insert
            rid = Employee.create( **request.form
            )

            return f'inserted {rid}'


app.run(host='0.0.0.0', port=8000, debug=True)    

