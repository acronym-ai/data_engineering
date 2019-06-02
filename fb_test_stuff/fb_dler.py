import json
import urllib
import subprocess
import warnings
import time

import pandas as pd

from datetime import date, timedelta
from collections import defaultdict as dd

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

with open('fb_cnfg.json') as jf:
  c = json.load(jf)

def get_fb_token(app_id, app_secret):
  oauth_args = {'client_id':app_id,
                'client_secret':app_secret,
                'grant_type':'client_credentials'}
  oauth_cmd = ['curl',
               'https://graph.facebook.com/oauth/access_token?' +
                urllib.parse.urlencode(oauth_args)]
  oauth_response = subprocess.Popen(oauth_cmd,
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE).communicate()[0]
  try:
    token = json.loads(oauth_response)['access_token']
    return token
  except KeyError:
    print('Bad OAuth response: {}'.format(str(oauth_response)))

FacebookAdsApi.init(c['fb_app_id'],c['fb_app_secret'],c['fb_access_token'])

num_days = 5
my_account = AdAccount(c['fb_account'])

fields = ['account_id',
          'account_name',
          'ad_id',
          'adset_id',
          'adset_name',
          'campaign_id',
          'campaign_name',
          'cost_per_outbound_click',
          'outbound_clicks',
          'outbound_clicks_ctr',
          'spend',
          'relevance_score',
          'actions']

tf = '%Y-%m-%d'

start = date.today() - timedelta(days=num_days)

while start < date.today():

  results = dd(dict)
  params = {'time_range':{'since':start.strftime(tf),'until':(start + timedelta(days=1)).strftime(tf)},'level':'ad'}

  ads = my_account.get_insights(params=params, fields=fields)
  for ad in ads:
    for f in fields:
      try:
        if type(ad[f]) == str:
          results[ad['ad_id']][f] = ad[f]
        elif f == 'relevance_score':
          results[ad['ad_id']][f] = ad[f]['score']
        elif type(ad[f]) == list:
          if len(ad[f]) == 1:
            results[ad['ad_id']][f] = ad[f][0]['value']
          else:
            for d in ad[f]:
              results[ad['ad_id']][d['action_type']] = d['value']
      except KeyError:
        print(f, )
    
  df = pd.DataFrame(results).T
  df.to_csv('pylon/d{}.csv'.format(start.strftime(tf)))

  start += timedelta(days=1)
  time.sleep(5)

print('all done!')
