from flask import Flask, render_template, Response, jsonify
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
import db
import simplejson
from operator import itemgetter

from collections import defaultdict

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
#db = SQLAlchemy(app)


@app.route("/")
def index():
    #results = db.get_opps()
    metrics = db.get_cam_metrics()

    return render_template('index.html',  metrics=metrics)

@app.route("/rollup", methods=['GET'])
def rollup():
    if request.method == 'GET':
      account_id = request.args.get('search', '')
    else:
      account_id = False
    metrics = db.get_rollup_metrics(account_id)

    return render_template('rollup.html', metrics=metrics)

@app.route("/map")
def map():

  return render_template('map.html')

@app.route("/sadscientists")
def do():
  results = db.inactive_users()
  # Get Summary Metrics
  metrics = db.get_inactive_user_metrics(results)
  # Sort by MRR
  sorted_results = sorted(results, key=itemgetter('price'), reverse=True)
  
  return render_template("non_active_users.html", results=sorted_results, metrics=metrics)

@app.route("/sfsadscientists")
def do_it():
  results = db.inactive_users()
  opp_ids = []
  for row in results:
    row['Id'] = row['id']
    opp_ids.append(row['Id'])
  soql_opps = ', '.join("'" + item + "'" for item in opp_ids) 
  details = db.sf_inactive_users(soql_opps)
  # Get Summary Metrics
  metrics = db.get_inactive_user_metrics(details)
  # Join results together
  d = defaultdict(dict)
  for l in (results, details):
    for elem in l:
       d[elem['Id']].update(elem)
  l3 = d.values()
  # Sort by MRR
  sorted_results = sorted(l3, key=itemgetter('Contracted_MRR__c'), reverse=True)
  
  return render_template("non_active_users.html", results=sorted_results, metrics=metrics)



@app.route("/results")
def results():
  results = db.get_opps()
  simplejson.dumps(results)

  return jsonify(data=results)

@app.route("/details", methods=['GET'])
def details():
  if request.method == 'GET':
      opp_id = request.args.get('opp_id')
      query = request.args.get('q')
  if query:
    details = db.get_opp_details(opp_id, query)
  else:
    details  = db.get_opp_details(opp_id)

  return render_template('details.html',  details=details, opp_id=opp_id)

@app.route("/search", methods=['GET'])
def search_experiences():
  if request.method == 'GET':
      query = request.args.get('q')

  results = db.search_experiences(query)

@app.route("/test")
def test():
  results = db.sf_api()
  return 'hi %s' % results

@app.route('/idiot', methods=['GET'])
def render_idiot():
    return render_template('test.html')

@app.route('/add_idiot', methods=['POST'])
def add_user():
    if request.method == 'POST':
        user = request.form['user']
        db.add_user(user)
    return Response(status=200)


@app.route("/vote", methods=['POST'])
def vote():
    if request.method == 'POST':
        vote = request.form['vote']
        user = request.form['user']
        db.set_vote(vote, user)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, port=6060)
