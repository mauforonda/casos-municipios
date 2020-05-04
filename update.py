#!/usr/bin/env python3

import requests
import pandas as pd
from datetime import datetime, timedelta
import os

def get_data():
  url = "https://cartocdn-gusc-a.global.ssl.fastly.net/datosagt2020/api/v1/map/datosagt2020@3d4d59de@a9396f47b03afc77e0bd604e238c4cee:1588558261126/dataview/3251a68b-6892-4205-85d8-1d7452aa3ec0/search?q={}"
  data = {}
  for i in ['a','e','i','o','u']:
    response = requests.get(url.format(i)).json()
    for c in response['categories']:
      if not data.__contains__(c['category']):
        data[c['category']] = c['value']
  return [[d, data[d]] for d in data.keys()]
  
def get_last_day_total():
  last_day = sorted(os.listdir('data'))[-1]
  return pd.read_csv('data/{}'.format(last_day))['confirmados'].sum()
  
def save(data):
  yesterday = (datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')
  filename = 'data/{}.csv'.format(yesterday)
  data.to_csv(filename, index=False)
  print(yesterday)

def update():
  data = pd.DataFrame(get_data(), columns=['municipio', 'confirmados'])
  last_day_total = get_last_day_total()
  if data['confirmados'].sum() != last_day_total:
    save(data)
  else:
    print('Nah')

update()
