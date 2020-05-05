#!/usr/bin/env python3

import requests
import pandas as pd
from datetime import datetime, timedelta
import os


def get_token():
  header = requests.head('https://datosagt2020.carto.com/api/v1/map/named/tpl_c1cdf57c_a007_4f3f_883a_c25ebdc50986/jsonp?lzma=3YCAiIDyhYCAgICAgIC9CAjntIUbMkyt4S6xq5e9KCiZiA%2Fk16XZNpEjL0UplWZ1Q%2F1d7Fye2NPgniOX6CgsAt7%2BHcooKUp7zxNcHAQxjE7ghggv7SVsQbnZW%2BJxAePj8e2OeJbR0tNGq%2BB1ZTm%2BdHihFuKnAg65TXhJ2dsZ6s4QY9Sc960%2FHSjyRlU%2FUiCYKlG4AwtF9iGZ0T%2FmRcPuf8g3uOguLATGs65XkSpUiEU7vWmAt6DQ2ePzQDWFQ%2Ftv9TGLepWuOQZPMQmtY%2Fmduz%2FtZL7L%2BwCQUXrZRIevrZpRAMEsc4uwI4rIdhzzQSgPdpCe7vr%2FiD%2BEOTsNAeMdJ2UgNQ6f3iMFWcZOR2u0NKBTqJ6ZlSMwQJzDleYZAUaNGxn%2FR60q0wx2OKY%2FWfgavbOc%2FkCNbi8wiplbIOUpvC%2FPVm5Kb%2BQ%2B3pycKbeXcmzP8K0bWlbvaO1TjYIxzQ8FMgUlxl9HRMqGaEW6bOCuPYRFsGRRLB43c3d35wddve4quWsRvOPOVgueuVcpovEMLwbXN3d8Hl6iBmaMXfdALGmVcL%2FabaZ2zgW14plnfXbnZMsuU8aJxryArxjUBwf2WHhEC8TI2cVe0CX6DO3oRryadzHcYMrE1UOPmzBxKF61AFXZnz4onOwbTVkDsf%2BilTsFf%2BK6E4A%3D&callback=_cdbc_3786648265_1').headers['X-Layergroup-Id']
  return header.split('@')[-1].split(':')

def get_data():
  token, calltime = get_token()
  url = "https://cartocdn-gusc-a.global.ssl.fastly.net/datosagt2020/api/v1/map/datosagt2020@3d4d59de@{t}:{c}/dataview/3251a68b-6892-4205-85d8-1d7452aa3ec0/search?q={q}"
  data = {}
  for i in ['a','e','i','o','u']:
    response = requests.get(url.format(q=i, c=calltime, t=token)).json()
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
