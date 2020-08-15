#!/usr/bin/env python3

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import rcParams
import time
import os
import unicodedata
import re
import requests

def intro(current):
  txt = [
    '> Casos confirmados de covid19 en Bolivia por municipio, de acuerdo a [esta visualización](https://datosagt2020.carto.com/builder/c1cdf57c-a007-4f3f-883a-c25ebdc50986/embed) mantenida por agetic datos',
    '_Actualizado el {a} con datos hasta el {u}_'.format(a=datetime.today().strftime('%Y/%m/%d'), u=current.split('.')[0].replace('-','/')),
    '## Casos por municipio']
  with open('readme.md', 'w+') as f:
    f.write('\n\n'.join(txt) + '\n\n')

def make_plot(name, series):
  # valid_name = unicodedata.normalize('NFKD', re.sub('[ \'\"]', '', name)).encode('ascii', 'ignore').decode('utf8')
  output = 'plots/{}.png'.format(name)
  fig = series.sort_index().plot(figsize=(1,0.3), rot=0, legend=False, color='#e23e57', linewidth=2).get_figure()
  plt.box(False)
  plt.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
  plt.grid(False)
  plt.savefig(output, bbox_inches='tight')
  plt.close()
  return output

def tendencias():
  days = sorted(os.listdir('clean_data'), reverse=True)
  df = pd.read_csv('clean_data/{}'.format(days[0]))[['cod_ine', 'municipio', 'confirmados']]
  df = df.set_index('cod_ine')
  for day in days[1:]:
    df2 = pd.read_csv('clean_data/{}'.format(day))[['cod_ine', 'confirmados']]
    df2 = df2.set_index('cod_ine')
    df = pd.concat([df, df2], axis=1, sort=False)
  df.columns = ['municipio'] + [day.split('.')[0] for day in days]
  df = df.fillna(0)
  df = df[df['municipio'] != 0]
  plots = []
  for i in range(0, len(df)):
    mun = df.iloc[i]
    mun_series = mun[1:]
    mun_series.index = pd.to_datetime(mun_series.index)
    plots.append(make_plot(str(mun.name), mun_series))
  return days[0], plots

def write_md(current, plots):
  intro(current)
  df = pd.read_csv('clean_data/{}'.format(current))
  df['tendencia'] = ['<img src="{}"/>'.format(p) for p in plots]
  df = df[['cod_ine', 'departamento', 'municipio', 'confirmados', 'tendencia', 'recuperados', 'decesos']]
  df = df.sort_values('confirmados', ascending=False)
  headers = ['INE', 'Departamento', 'Municipio', 'Confirmados', 'Tendencia', 'Recuperados', 'Decesos']
  with open('readme.md', 'a') as f:
    df.to_markdown(f, tablefmt='github', showindex=False, headers=headers)

def update_data(tablename):
  ultimo_dia = datetime.strptime(sorted(os.listdir('clean_data'))[-1].split('.')[0], '%Y-%m-%d')
  datos = pd.read_csv('https://datosagt2020.carto.com/api/v2/sql?filename={}&q=SELECT+*+FROM+(select+*+from+public.mun_covid_se31)+as+subq+&format=csv&bounds=&api_key=&skipfields=the_geom_webmercator'.format(tablename))
  dia = datetime.strptime('2020 6 {}'.format(str(datos.se[0] - 1)), '%Y %w %U')
  if dia > ultimo_dia:
    datos = datos[['codigo', 'confirmados', 'recuperados', 'fallecidos']]
    datos.index = datos['codigo']
    poblacion = pd.read_csv('context/poblacion.csv', index_col='cod_ine')[['departamento', 'municipio']]
    df = pd.concat([poblacion, datos], axis=1).dropna()
    df[['codigo', 'confirmados', 'recuperados', 'fallecidos']] = df[['codigo', 'confirmados', 'recuperados', 'fallecidos']].astype(int)
    df.to_csv('clean_data/{}.csv'.format(dia.strftime('%Y-%m-%d')), header=['departamento', 'municipio', 'cod_ine', 'confirmados', 'recuperados', 'decesos'], float_format='%0.f', index=False)   
    current, plots = tendencias()
    write_md(current, plots)
    print(dia.strftime('%Y-%m-%d'))
  else:
    print(0)

def fin_de_semana(semana):
  return datetime.strptime('2020 6 {}'.format(str(int(semana) - 1)), '%Y %w %U')

def check_source():
  ultimo_dia = datetime.strptime(sorted(os.listdir('clean_data'))[-1].split('.')[0], '%Y-%m-%d')
  response = requests.get('https://datosagt2020.carto.com/api/v1/viz?types=table,derived&privacy=public&only_published=true&exclude_shared=true&per_page=10&order=updated_at&page=1').json()
  for entry in response['visualizations']:
    if entry['type'] == 'table' and 'mun_covid' in entry['name'] and fin_de_semana(entry['name'].split('_se')[1]) > ultimo_dia:
      update_data(entry['name'])

check_source()
