from sqlalchemy import *
import beatbox
from operator import itemgetter
from datetime import date
import datetime

TODAY = date.today()
EOQ_DATE = date(TODAY.year, 12, 30)
BOQ_DATE = date(TODAY.year, 10, 1)
TARGET = 800000
USERNAME = ''
PASSWORD = ''

def sf_api():
  svc = beatbox.PythonClient()
  svc.login(USERNAME, PASSWORD)

  return svc

def get_opps():
  svc = sf_api()
  opps = svc.query("SELECT Id, Name, Client_Total__c, StageName, Event_Date__c, Primary_Contact_First_Name__c, Primary_Contact_Last_Name__c, Number_of_Pitched_Experiences__c from Opportunity WHERE StageName NOT IN ('On Hold', 'Overages', 'Closed Lost') AND Number_of_Pitched_Experiences__c > 0.0 AND OwnerId = '005C0000009qrjxIAA' AND CloseDate <= THIS_QUARTER")
  for row in opps:
    row['Contact_Name'] = '%s %s' % (row['Primary_Contact_First_Name__c'], row['Primary_Contact_Last_Name__c'])
    row['Event_Date__c'] = str(row['Event_Date__c'])

  results = sorted(opps, key=itemgetter('Event_Date__c'))

  return results

def get_opp_details(opp_id, search_query=False):
  svc = sf_api()
  query = "SELECT experience__c from pitched_experiences__c WHERE opportunity__c ='%s'" % opp_id
  pitches = svc.query(query)
  pitch_ids = []
  for pitch in pitches:
    pitch_ids.append(pitch['Experience__c'])
  exp_ids = "', '".join(map(str, pitch_ids))
  exp_query = "SELECT name, Id, Total_Client_Cost_Per_Guest__c FROM Event_Package__c WHERE id IN ('%s')" % exp_ids

  experiences = svc.query(exp_query)

  if search_query:

    results = search_experiences(query)

  return experiences

def search_experiences(query):
  svc = sf_api()
  query = "SELECT Name, Available_Markets__c, Bar_Highlights__c, Cost__c, Max_Capacity__c, Min_Capacity__c, Package_URL__c, Type FROM Event_Package__c WHERE Name LIKE '%%s%%'" % query
  results = svc.query(query)
  print results
  for row in results:
    print row
  return results

def get_cam_metrics():
  results = get_opps()
  total_rev = 0
  total_opps = len(results)
  closed_rev = 0
  # Stage Counts
  gathering_info = 0
  options_sent = 0
  options_high = 0
  event_selected = 0
  pl_sent = 0
  pending_payment = 0
  partial_funds = 0
  funds_received = 0
  closed_won = 0
  closed_lost = 0
  for row in results:
      total_rev += row['Client_Total__c']
      if row['StageName'] == 'Gathering Information':
        gathering_info += 1
      if row['StageName'] == 'Options Sent to Client':
        options_sent += 1
      if row['StageName'] == 'Options Sent to High':
        options_high += 1
      if row['StageName'] == 'Event Selected':
        event_selected += 1
      if row['StageName'] == 'PL Sent':
        pl_sent += 1
      if row['StageName'] == 'Pending Customer Payment':
        pending_payment += 1
      if row['StageName'] == 'Partial Funds Received':
        partial_funds += 1
        closed_rev += row['Client_Total__c']
      if row['StageName'] == 'Funds Received - Sign Contracts':
        funds_received += 1
        closed_rev += row['Client_Total__c']
      if row['StageName'] == 'Closed Won':
        closed_won += 1
        closed_rev += row['Client_Total__c']
      if row['StageName'] == 'Closed Lost':
        closed_lost += 1
  metrics = {}
  metrics['total_rev'] = total_rev
  metrics['total_opps'] = total_opps
  metrics['gathering_info'] = gathering_info
  metrics['options_sent'] = options_sent
  metrics['options_high'] = options_high
  metrics['event_selected'] = event_selected
  metrics['pl_sent'] = pl_sent
  metrics['pending_payment'] = pending_payment
  metrics['partial_funds'] = partial_funds
  metrics['funds_received'] = funds_received
  metrics['closed_won'] = closed_won
  metrics['closed_lost'] = closed_lost
  metrics['closed_rev'] = closed_rev
  target_difference = TARGET - closed_rev
  days_in_q = (TODAY - BOQ_DATE).days
  days_left_in_q = (EOQ_DATE - TODAY).days
  potential_rev = (closed_rev/days_in_q)*days_left_in_q
  metrics['run_rate'] = round((potential_rev + closed_rev) / TARGET * 100, 4)

  return metrics

def get_rollup_metrics(account_id=None):
  svc = sf_api()
  if account_id:
    query = "SELECT Name, Market__c, event_date__c, event_type__c, attendees__c, nps_score__c, total_cost_per_person__c, total_paid__c from opportunity where accountid = '%s' and StageName = 'Closed Won'" % account_id
    name_query = "SELECT Name FROM Account WHERE Id = '%s'" % account_id
  else:
    # Lenovo
    query = "SELECT Name, Market__c, event_date__c, event_type__c, attendees__c, nps_score__c, total_cost_per_person__c, total_paid__c from opportunity where accountid = '001C000001BVIUnIAP' and StageName = 'Closed Won'"
    name_query = "SELECT Name FROM Account WHERE Id = '001C000001BVIUnIAP'"

  results = svc.query(query)
  name = svc.query(name_query)
  metrics = {}
  total_revenue = 0
  total_events = 0
  avg_nps = 0
  nps_total = 0
  nps_count = 0
  event_types = {}
  team_outing = 0
  marketing = 0
  other = 0
  attendees = 0
  line = []
  for opp in results:
    event_dates = {}
    event_dates['date'] = datetime.datetime.strftime(opp['Event_Date__c'], '%Y-%m-%d')
    event_dates['attendees'] = opp['Attendees__c'] if opp['Attendees__c'] else 0
    line.append(event_dates)
    total_revenue += opp['Total_Paid__c']
    total_events += 1
    if opp['Attendees__c']:
      attendees += opp['Attendees__c']
    if opp['NPS_Score__c']:
      nps_total += opp['NPS_Score__c']
      nps_count += 1.0
    if opp['Event_Type__c'] == 'Team Outing':
       team_outing += 1
    if opp['Event_Type__c'] == 'Marketing/Client Entertainment':
       marketing += 1
    if opp['Event_Type__c'] == 'Other':
       other += 1
  pie = [{'type':'Marketing', 'value': marketing},{'type':'Team Outing', 'value':team_outing}, {'type':'Other', 'value':other}]

  print line
  avg_nps = nps_total/nps_count
  metrics['avg_nps'] = round(avg_nps, 2)
  metrics['pie'] = pie
  metrics['line'] = line
  metrics['total_events'] = total_events
  metrics['total_rev'] = total_revenue
  metrics['attendees'] = attendees
  metrics['name'] = name[0]['Name']

  return metrics

def stupid():
  return requests.get('https://cs7.salesforce.com/services/apexrest/ExperienceFinancial?opportunityId=0063B000002GJaP&experienceId=1111&experienceName=test&experienceParentId=111111').content
