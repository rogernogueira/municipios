import pandas as pd
import numpy as np
import configparser
import geojson
import geopandas as gpd
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
ANO = int(config['DEFAULT']['ANO'])
INDICADORES = config['DEFAULT']['Indicadores'].split(',')
SIGLA_ESTADO = config['DEFAULT']['SIGLA_ESTADO']

df = pd.read_excel('data\\Base2022.xlsx')
df_regioes = pd.read_excel('data/regionalizacao.xlsx')
df = df[df['estado (sigla)'] == SIGLA_ESTADO]
df = df.merge(df_regioes, on='Código IBGE', how='left')                                                

df.rename(columns={
    'IGM/CFA':'IGM',
    'Finanças - Dimensão':'Finanças',
    'Gestão - Dimensão':'Gestão',
    'Desempenho - Dimensão':'Desempenho',
    'Dados de Identificação/Demográficos - População':'População',
    'Nome da Mesorregião':'Mesorregião',
    'Nome da Microrregião':'Microrregião',
       }, inplace=True)

with open('assets/to_municipios.json', encoding='utf-8') as f:
    geojson_municipios = geojson.load(f)

#iterar sobre dataframe 
for feature in geojson_municipios['features']:  
    for index, row in df[df['ano']==ANO].iterrows():
        if feature['properties']['id'] == str(row['Código IBGE']):
            feature['properties']['tooltip'] = row['nome']
            feature['properties']['Mesorregião'] = row['Mesorregião']
            feature['properties']['Microrregião'] = row['Microrregião']
            feature['properties']['Intermediária'] = row['Intermediária']
            feature['properties']['Imediata'] = row['Imediata']
            

            feature['properties']['Cluster'] = row['Cluster']  
            for i in INDICADORES:
                feature['properties'][i] = row[i]


gpd_municipios = gpd.GeoDataFrame.from_features(geojson_municipios)
gpd_municipios['id'] = gpd_municipios['id'].apply(lambda x : int(x))

df = pd.merge(df, gpd_municipios[['id','name']], how="outer", left_on='Código IBGE', right_on='id')
df.drop(columns=['nome'], inplace=True)
df.rename(columns={'name':'nome'}, inplace=True)
df.drop(columns=['id'], inplace=True)
df.to_pickle('data/df_tocantins.pkl')

import geopandas as gpd
df_tpm =gpd.GeoDataFrame.from_features(geojson_municipios)
df_tpm.rename(columns={'name':'nome'}, inplace=True)
df_tpm.set_index('nome', inplace=True)
df_tpm.to_file('data/geo_municipios.json', driver="GeoJSON")


