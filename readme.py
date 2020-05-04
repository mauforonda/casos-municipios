#!/usr/bin/env python3

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import rcParams
import time
import os

def make_table(df):
  view = []
  codigos = pd.read_csv('context/cod_ine.csv')
  population = pd.read_csv('context/poblacion.csv')
  for row in range(0,len(df)):
    mun = df.iloc[row]
    path = make_plot(mun.name, mun)
    cod_ine = codigos[codigos['municipio'] == mun.name]['cod_ine'].values
    if len(cod_ine) == 0:
      cod_ine, pop, proportion = [0] * 3
    else:
      cod_ine = cod_ine[0]
      pop = int(population[population['cod_ine'] == cod_ine]['poblacion'].values[0])
      proportion = (mun[0] / pop) * 100
    view.append([mun.name,
                 int(mun[0]),
                 int(mun[0] - mun[1]),
                 int(mun[0] - mun[-1]),
                 pop,
                 proportion,
                 '<img src="{}"/>'.format(path)])
  with open('readme.md', 'a') as f:
    pd.DataFrame(view, columns=['Municipio', 'Confirmados', 'Último Día', 'Desde {}'.format(df.columns[-1]), 'Población', '% Infectado', 'Tendencia']).sort_values('Desde {}'.format(df.columns[-1]), ascending=False).to_markdown(f, tablefmt='github', showindex=False, floatfmt=".3f")

def make_plot(name, series):
  output = 'plots/{}.png'.format(name.strip().lower().replace(" ", "-"))
  fig = series.sort_index().plot(figsize=(1,0.3), rot=0, legend=False, color='#e23e57', linewidth=2).get_figure()
  plt.box(False)
  plt.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
  plt.grid(False)
  plt.savefig(output, bbox_inches='tight')
  plt.close()
  return output

def get_file_list():
  last_week = [(datetime.today() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1,8)]
  return [day for day in last_week if os.path.isfile('data/{}.csv'.format(day))]

def make_dataframe(days):
  df = pd.read_csv('data/{}.csv'.format(days[0]))
  df = df.set_index('municipio')
  for day in days[1:]:
    df2 = pd.read_csv('data/{}.csv'.format(day))
    df2 = df2.set_index('municipio')
    df = pd.concat([df, df2], axis=1, sort=False)
  df.columns = days
  return df.fillna(0)

def intro():
  txt = [
    '> Casos confirmados de covid19 en Bolivia por municipio, de acuerdo a [esta visualización](https://datosagt2020.carto.com/builder/c1cdf57c-a007-4f3f-883a-c25ebdc50986/embed) mantenida por agetic datos',
    '_Actualizado el {}_'.format(datetime.today().strftime('%Y/%m/%d')),
    'Ordenados por el número de casos en la última semana.']
  with open('readme.md', 'w+') as f:
    f.write('\n\n'.join(txt) + '\n\n')

def outro():
  txt = [
    'Los datos hasta el 30 de abril provienen de esta [otra visualización](https://juliael.carto.com/builder/c70fa175-3e6a-4955-8088-89048c6e6886/embed) de agetic.']
  with open('readme.md', 'a') as f:
    f.write('\n\n---\n\n' + '\n\n'.join(txt))
    
intro()
days = get_file_list()
df = make_dataframe(days)
make_table(df)
outro()

