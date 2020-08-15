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
    '_Actualizado el {a} con datos hasta el {u}_'.format(a=datetime.today().strftime('%Y/%m/%d'), u=current.strftime('%Y/%m/%d'))]
  with open('readme.md', 'w+') as f:
    f.write('\n\n'.join(txt) + '\n\n')

def write_md(current, plots):
  intro(current)

def update_data(tablename):
  dia = fin_de_semana(tablename.split('_se')[1])
  datos = pd.read_csv('https://datosagt2020.carto.com/api/v2/sql?filename={t}&q=SELECT+*+FROM+(select+*+from+public.{t})+as+subq+&format=csv&bounds=&api_key=&skipfields=the_geom_webmercator'.format(t=tablename))
  datos = datos[['codigo', 'confirmados', 'recuperados', 'fallecidos']]
  datos.index = datos['codigo']
  poblacion = pd.read_csv('context/poblacion.csv', index_col='cod_ine')[['departamento', 'municipio']]
  df = pd.concat([poblacion, datos], axis=1).dropna()
  df[['codigo', 'confirmados', 'recuperados', 'fallecidos']] = df[['codigo', 'confirmados', 'recuperados', 'fallecidos']].astype(int)
  df.to_csv('clean_data/{}.csv'.format(dia.strftime('%Y-%m-%d')), header=['departamento', 'municipio', 'cod_ine', 'confirmados', 'recuperados', 'decesos'], float_format='%0.f', index=False)   
  write_md(dia)
  print(dia.strftime('%Y-%m-%d'))

def fin_de_semana(semana):
  return datetime.strptime('2020 6 {}'.format(str(int(semana) - 1)), '%Y %w %U')

def check_source():
  ultimo_dia = datetime.strptime(sorted(os.listdir('clean_data'))[-1].split('.')[0], '%Y-%m-%d')
  response = requests.get('https://datosagt2020.carto.com/api/v1/viz?types=table,derived&privacy=public&only_published=true&exclude_shared=true&per_page=10&order=updated_at&page=1').json()
  new_tables = [entry['name'] for entry in response['visualizations'] if entry['type'] == 'table' and 'mun_covid' in entry['name'] and fin_de_semana(entry['name'].split('_se')[1]) > ultimo_dia]
  if len(new_tables) > 0:
    update_data(new_tables[0])
  else:
    print(0)

check_source()
