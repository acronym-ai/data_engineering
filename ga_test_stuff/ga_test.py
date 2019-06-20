from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

scopes = ['https://www.googleapis.com/auth/analytics.readonly']

key_path = '/home/ec2-user/scripts/data_engineering/ga_test_stuff/ga.json'
view_id = '95396115'

def initialize_analyticsreporting():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
    key_path, scopes)

  analytics = build('analyticsreporting','v4',credentials=credentials)
  return analytics

def get_report(analytics):
  return analytics.reports().batchGet(
    body={'reportRequests': [
           {'viewId': view_id, 'dateRanges':[{'startDate':'7daysAgo','endDate':'today'}],
            'metrics': [{'expression':'ga:sessions'}], 'dimensions':[{'name':'ga:country'}]}]}
    ).execute()

def print_response(response):
  for report in response.get('reports', []):
    column_header = report.get('columnHeader', {})
    dimension_headers = column_header.get('dimensions', [])
    metric_headers = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])
  
    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      date_range_values = row.get('metrics', [])
  
      for header, dimension in zip(dimension_headers, dimensions):
        print(header + ': ' + dimension)
  
      for i, values in enumerate(date_range_values):
        print('Date Range: ' + str(i))
        for metric_header, value in zip(metric_headers, values.get(values)):
          print(metric_header.get('name') + ': ' + value)

def print_response2(response):
  for report in response.get('reports', []):
    print(report)

## and here we go!

def main():
  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  print_response2(response)

if __name__ == '__main__':
  main()
