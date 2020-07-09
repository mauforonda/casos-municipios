#!/usr/bin/env python3

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import rcParams
import time
import os
import unicodedata
import re

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

current, plots = tendencias()
write_md(current, plots)

