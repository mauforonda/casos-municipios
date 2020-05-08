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
  riesgos = pd.read_csv('context/riesgo.csv')
  for row in range(0,len(df)):
    mun = df.iloc[row]
    path = make_plot(mun.name, mun)
    cod_ine = codigos[codigos['municipio'] == mun.name]['cod_ine'].values
    if len(cod_ine) == 0:
      cod_ine, riesgo, indice, dep, pop, perthous = [0] * 6
    else:
      cod_ine = cod_ine[0]
      riesgo, indice = riesgos[riesgos['cod_ine'] == cod_ine][['riesgo','indice']].values.tolist()[0]
      dep, pop = population[population['cod_ine'] == cod_ine][['departamento', 'poblacion']].values.tolist()[0]
      pop = int(pop)
      perthous = int((mun[0] / pop) * 1000000)
    view.append([dep,
                 mun.name,
                 int(mun[0]),
                 int(mun[0] - mun[1]),
                 int(mun[0] - mun[-1]),
                 riesgo,
                 indice,
                 perthous,
                 '<img src="{}"/>'.format(path)])
  view_cols = ['Departamento', 'Municipio', 'Confirmados', 'Último Día', 'Desde {}'.format(df.columns[-1]), 'Riesgo', 'Índice', 'Casos por millón de habitantes', 'Tendencia']
  view_df = pd.DataFrame(view, columns=view_cols).sort_values('Casos por millón de habitantes', ascending=False)
  with open('readme.md', 'a') as f:
    view_df.to_markdown(f, tablefmt='github', showindex=False, floatfmt=".3f")
  with open('dashboard.csv', 'w+') as f:
    view_df.to_csv(f, index=False, columns = view_cols[:-1])

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

def intro(days):
  txt = [
    '> Casos confirmados de covid19 en Bolivia por municipio, de acuerdo a [esta visualización](https://datosagt2020.carto.com/builder/c1cdf57c-a007-4f3f-883a-c25ebdc50986/embed) mantenida por agetic datos',
    '_Actualizado el {a} con datos hasta el {u}_'.format(a=datetime.today().strftime('%Y/%m/%d'), u=days[0].replace('-','/')),
    'Ordenados por el número de casos por millón de habitantes.']
  with open('readme.md', 'w+') as f:
    f.write('\n\n'.join(txt) + '\n\n')

def outro():
  txt = [
    '- Los datos hasta el 30 de abril provienen de esta [otra visualización](https://juliael.carto.com/builder/c70fa175-3e6a-4955-8088-89048c6e6886/embed) de agetic.',
    '- Los índices de riesgo fueron publicados el 7 de mayo por el gobierno en [este pdf](https://www.minsalud.gob.bo/images/Descarga/covid19/Indice_Riesgo_Municipal_070520.pdf)',
    '- Existen muchas irregularidades en los nombres de municipios provistos por la fuente de datos de casos. Por eso prefiero construir un diccionario manual de códigos ine. Eso significa que cuando se registre un caso en un nuevo municipio, las columnas de contexto estarán temporalmente vacías.',
    '- Puedes descargar los datos de la tabla de encima en [este enlace](https://raw.githubusercontent.com/mauforonda/casos-municipios/master/dashboard.csv)']
  with open('readme.md', 'a') as f:
    f.write('\n\n---\n\n' + '\n\n'.join(txt))
    
days = get_file_list()
intro(days)
df = make_dataframe(days)
make_table(df)
outro()

