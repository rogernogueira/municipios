import pandas as pd
import json
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, Output, Input, dcc, State
from dash_extensions.javascript import arrow_function
from dash_extensions.javascript import assign, Namespace
import geojson
import plotly.express as px
import plotly.graph_objects as go
import dash

from unidecode import unidecode
from templates.menu import  custom_default
import babel.numbers
external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css']
chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js" 
# colorscale = [ '#304d63','#ED8975', '#8fb9aa', '#FD8D3C', ]
# color_prop = 'IGM'
# style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

# df_tocantins = pd.read_pickle('data/tocantins.pkl')
# #df_tocantins.rename(columns={'IGM/CFA':'IGM', 'Finanças - Dimensão':'Finanças','Gestão - Dimensão':'Gestão','Desempenho - Dimensão':'Desempenho'   }, inplace=True)
# #df_tocantins.to_pickle('data/tocantins.pkl')
# # # ano de 2021
# # df_tocantins_ano = df_tocantins[df_tocantins['ano'] == 2021][['nome', "Código IBGE","IGM/CFA",'Finanças - Dimensão','Gestão - Dimensão','Desempenho - Dimensão', 'Cluster']]	
# # df_tocantins_ano.rename(columns={'IGM/CFA':'IGM', 'Finanças - Dimensão':'Finanças','Gestão - Dimensão':'Gestão','Desempenho - Dimensão':'Desempenho'   }, inplace=True)

# # #save to pickle

# df_tocantins_ano = pd.read_pickle('data/tocantins_2021.pkl')


# ranking_geral = df_tocantins_ano.sort_values(['IGM'],ascending=False )['nome'].tolist()
# ranking_geral = dict(zip(ranking_geral,range(1,len(ranking_geral)+1)))

# list_municipios = df_tocantins_ano[['nome','Código IBGE']].groupby('nome').first().reset_index()
# dict_municipios = dict(zip(list_municipios['nome'], list_municipios['Código IBGE']))

# df_cidade_ibge = pd.read_json('data/cidades.json')
# df_cidade_to = df_cidade_ibge[df_cidade_ibge['codigo_uf']==17]

# df_cidade_to = df_cidade_to.merge(df_tocantins_ano, left_on='codigo_ibge', right_on='Código IBGE')
# dict_cidade_to = df_cidade_to.to_dict('records') 

# for item in dict_cidade_to:
#         item["tooltip"] = f"{item['nome_x']} "

# with open('assets/to_municipios.json', encoding='utf-8') as f:
#     geojson_municipios = geojson.load(f)

# for feature in geojson_municipios['features']:
#     for item in dict_cidade_to:
#         if feature['properties']['id'] == str(item['codigo_ibge']):
#             feature['properties']['tooltip'] = item['tooltip']
#             feature['properties']['IGM'] = item['IGM']
#             feature['properties']['Finanças'] = item['Finanças']
#             feature['properties']['Desempenho'] = item['Desempenho']
#             feature['properties']['Gestão'] = item['Gestão']
 
# #colorbar = dl.Colorbar(colorscale=colorscale, width=20, height=150, min=min, max=max, unit=' IGM/CFA')

# # classes = df_cidade_to[color_prop].quantile([0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]).tolist()    
# classes = (0,2.5,5,7.5,10)
# # ctg = ["{}".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}".format(classes[-1])]
# ctg = ['0-2.5', '2.5-5', '5-7.5', '7.5-10']
# colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, unit='IGM', position='bottomleft')



# style_handle = assign("""function(feature, context){
#     const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
#     const value = feature.properties[colorProp];  // get value the determines the color
#     for (let i = 0; i < classes.length; ++i) {
#         if (value > classes[i]) {
#             style.fillColor = colorscale[i];  // set the fill color according to the class
#         }
#     }
  
#     return style;
# }""")

# def get_map(color_prop):
#     return     dl.Map(center=[-9.407668341753798, -48.416790644617116], zoom=7, children=[
#                                         dl.TileLayer(),
#                                         dl.GeoJSON(data =geojson_municipios, format="geojson", id="cidades",
#                                                     options=dict(style=style_handle),
#                                                     zoomToBounds=True,
#                                                     zoomToBoundsOnClick=False,
#                                                     hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
#                                                     hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=color_prop),
#                                                 ),  
#                                         colorbar, 
#                                         info,  
#                                         # geobuf resource (fastest option)
#                                     ], style={'width': '100%', 'height': '90vh', 'margin': "auto", "display": "block"}, id="map")

# def ranking_municipio_grupo(nome):
#     cluster = df_tocantins_ano[df_tocantins_ano['nome'] == nome]['Cluster'].iloc[0]
#     list_cluster = df_tocantins_ano[df_tocantins_ano['Cluster'] == cluster].sort_values(['IGM'],ascending=False )['nome'].tolist()    
#     list_cluster = dict(zip(list_cluster,range(1,len(list_cluster)+1)))
#     return list_cluster[nome], cluster
    
# def get_info(feature=None, color_prop="IGM"):
#     header = [html.H4(f"{color_prop} - 2021")]
#     if not feature:
#         return header + [html.P("Passa o mouse sobre um município")]
#     return header + [html.B(feature["properties"]["name"]), html.Br(),
#                      "{:.3f}".format(feature["properties"][color_prop])]
# info = html.Div(children=get_info(), id="info", className="info",
#                 style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000"})


# def get_grafico_municipio(value, color_prop="IGM"):
#     df_result = df_tocantins[df_tocantins['Código IBGE'] == int(value)]
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['IGM'],
#                         mode='lines+markers',
#                         name='IGM'))
#     fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['Desempenho'],
#                         mode='lines+markers',
#                         name='Desempenho'))
#     fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['Finanças'],
#                         mode='lines+markers', name='Finanças'))
    
#     fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['Gestão'],
#                         mode='lines+markers', name='Gestão'))
#     fig.update_layout(title=f'Indicadores de {df_result["nome"].iloc[0]}',
#                    xaxis_title='Ano',
#                    yaxis_title='Valor do indicador')
#     annotations = []
#     annotations.append(dict(xref='paper', yref='paper', x=0.4, y=-0.2,
#                               xanchor='left', yanchor='top',
#                               text='Fonte: https://igm.cfa.org.br/',
#                               font=dict(family='Arial',
#                                         size=12,
#                                         color='rgb(150,150,150)'),
#                               showarrow=False))

#     fig.update_layout(annotations=annotations)

#     #fig = px.line(df_result, x="ano", y=color_prop, markers=True, title=f'Índice {color_prop} - {df_result[7"nome"].iloc[0]}')        
#     layout_result = html.Div([
#             dcc.Graph(figure=fig, id="graph"),            
#             ], className="w-100")
#     return html.Div([layout_result], className="container shadow  bg-body rounded d-flex ")

# def get_dados_municipio(value, color_prop="IGM"):
#     df_result = df_tocantins[df_tocantins['Código IBGE'] == int(value)]
#     nome_municipio  = df_result["nome"].iloc[0]
#     igm_municipio  = df_result[color_prop].iloc[0]
#     populacao_municipio  = df_result["Dados de Identificação/Demográficos - População"].iloc[0]
#     populacao_municipio = babel.numbers.format_number(populacao_municipio, locale='pt_BR')
#     pib_municipio  = df_result["Pib per capita 2020"].iloc[0]
#     pib_municipio = babel.numbers.format_currency(pib_municipio, 'BRL', locale='pt_BR')
#     posicao_geral = ranking_geral[nome_municipio]
#     posicao_grupo, grupo = ranking_municipio_grupo(nome_municipio)   
#     layout_result =  html.Div(
#                                 [
#                                     html.Div(
#                                         [html.H5(f"{nome_municipio}",className="card-title"),
#                                         html.H6(f"{color_prop} :{igm_municipio}",className="card-subtitle mb-2 text-muted"),
#                                         html.Div([
#                                             html.Div([
#                                                 html.H6(f"Posição no ranking TO : {posicao_geral}º ",id="",className=""), 
#                                                 html.H6(f"Posição no {grupo} : {posicao_grupo}º ",id="",className=""), 
#                                             ]),
#                                             html.Div([
#                                                 html.H6(f"PIB : {pib_municipio}  ",id="",className=""), 
#                                                 html.H6(f"População : {populacao_municipio} Hab.",id="",className=""), 
#                                             ]),
#                                         ], className="d-flex justify-content-between "),
#                                        ]),
#                                 ],
#                                 id="info-container",
#                                 className="container ",
#                             )
    
#     return html.Div([layout_result], className="container shadow  bg-body rounded d-flex mt-1 ")
app = Dash( suppress_callback_exceptions=True, 
            name=__name__,
            server=False,
            use_pages=True,
             pages_folder='pages',
            routes_pathname_prefix='/',    
            external_stylesheets=external_stylesheets, external_scripts=[chroma], prevent_initial_callbacks=True, assets_folder='/app/municipios/assets',
            title="IGM/CFA - 2021", )
#app = Dash( suppress_callback_exceptions=True, external_stylesheets=external_stylesheets, external_scripts=[chroma], prevent_initial_callbacks=True, assets_folder='assets',  title="IGM/CFA - 2021", use_pages=True, )


app.layout = html.Div([
                        custom_default,
                        dash.page_container,
                         
                        #      html.Div(
                        #                     [
                        #                         html.Div(
                        #                             dcc.Link(
                        #                                 f"{page['name']} - {page['path']}", href=page["relative_path"]
                        #                             )
                        #                         )
                        #                         for page in dash.page_registry.values()
                        #                     ]
                        #                 ),
                        # html.Div([
                        #         html.Div([      
                        #                     html.Label("Indicador:"),    
                        #                     dcc.Dropdown(
                        #                                         id='select_indicador',
                        #                                         options=['IGM', 'Finanças','Gestão','Desempenho'],
                        #                                         multi=False,
                        #                                         value='IGM',
                        #                                     ),
                        #                     html.Div([get_map("IGM")],id='layout_map' ),            
                        #                 ], id="dropdown_indicador",className='container shadow'),
        
                        #     html.Div([                             
                        #         html.Div([
                        #                    html.Div([      
                        #                    html.Label("Município:"),    
                        #                    dcc.Dropdown(
                        #                                     id='select_municipio',
                        #                                     options=list(dict_municipios.keys()),
                        #                                     multi=False,
                        #                                     value='PALMAS',
                        #                                 ),
                        #                         ], className="w-100"), 
                        #                  ], id="dropdown_cidades", className="p-2 mb-2 container shadow  bg-body rounded d-flex"),
                        #         html.Div(id="grafico_igm", className="container"),
                        #         html.Div(id="dados_municipio", className="container"),
                        #         dash.page_container,
                        #     ], className=" d-flex flex-column w-100")     
                        # ],
                        #  className="container shadow  bg-body rounded d-flex p-2 col-lg-12"),                
                        
])

# @app.callback(
#     Output("layout_map", "children"), 
#     [Input("select_indicador", "value")])
# def map_indicador(input_value):
#         return get_map(input_value)

# @app.callback(
#     Output("select_municipio", "value"), 
#     [Input("cidades", "click_feature")])
# def capital_click(feature):
#     if feature is not None:
#         return unidecode(feature['properties']['name'].upper())

# @app.callback(Output("info", "children"),
#               [Input("cidades", "hover_feature"), 
#                Input("select_indicador", "value")],)
# def info_hover(feature, color_prop="IGM"):
#     return get_info(feature, color_prop)

# @app.callback(
#     Output("grafico_igm", "children"),
#     Output("dados_municipio", "children"),
#     [Input('select_municipio','value'),
#     Input("select_indicador", "value")
#            ] ,
  
# )
# def update_output_div(input_value, color_prop="IGM",):
 
   
#     if input_value is not None:
#         return get_grafico_municipio(dict_municipios[input_value],color_prop), get_dados_municipio(dict_municipios[input_value], color_prop)
#     else:
#         return "", ""
# no servidor
server = app.server 


# if __name__ == '__main__':
#     app.run_server(debug=True)