import dash
import pandas as pd
import json
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, Output, Input, dcc, State, callback
from dash_extensions.javascript import arrow_function
from dash_extensions.javascript import assign, Namespace
import geojson
import plotly.express as px
import plotly.graph_objects as go
from unidecode import unidecode
from templates.menu import  custom_default
import babel.numbers
import configparser
import geopandas as gpd



dash.register_page(__name__, path='/')
external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css']
chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js" 
color_prop = 'IGM'
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

INDICADORES = config['DEFAULT']['Indicadores'].split(',')
ANO = int(config['DEFAULT']['ANO'])
colorscale = config['DEFAULT']['COLORSCALE'].split(',')

df_tocantins = pd.read_pickle('data/df_tocantins.pkl')

gpd_municipios=gpd.GeoDataFrame.from_file('data/geo_municipios.json', driver="GeoJSON")
geojson_municipios = geojson.loads(gpd_municipios.to_json())




def get_ranking_geral():
    ranking_geral = []
    for i in INDICADORES:
        df_ord = gpd_municipios.sort_values([i],ascending=False )['nome'].tolist()
        dict_rank_indicador =   dict(zip(df_ord,range(1,len(df_ord)+1)))
        ranking_geral.append(dict_rank_indicador)
    return ranking_geral




            
#colorbar = dl.Colorbar(colorscale=colorscale, width=20, height=150, min=min, max=max, unit=' IGM/CFA')

# classes = df_cidade_to[color_prop].quantile([0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]).tolist()    
classes = (0,2.5,5,7.5,10)
# ctg = ["{}".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}".format(classes[-1])]
ctg = ['0-2.5', '2.5-5', '5-7.5', '7.5-10']
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale[0:4], width=300, height=30, unit='IGM', position='bottomleft')



style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
  
    return style;
}""")

def get_map(color_prop, geojson_municipios_tmp):
    
    return html.Div([   
    
         dl.Map(center=[-9.407668341753798, -48.416790644617116], zoom=7, children=[
                                        dl.TileLayer(),
                                        dl.GeoJSON(data =geojson_municipios_tmp, format="geojson", id="cidades",
                                                    options=dict(style=style_handle),
                                                    zoomToBounds=True,
                                                    zoomToBoundsOnClick=False,
                                                    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
                                                    hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=color_prop),
                                                ),  
                                        colorbar, 
                                        info,  
                                        # geobuf resource (fastest option)
                                    ], style={'width': '100%', 'height': '80vh', 'margin':'auto', "display": "block", }, id="map")
    ], className="container shadow  bg-body rounded d-flex mt-1 ", style={'padding':'10px'})

def ranking_municipio_grupo(nome):
    cluster = gpd_municipios[gpd_municipios['nome'] == nome]['Cluster'].iloc[0]
    list_cluster = gpd_municipios[gpd_municipios['Cluster'] == cluster].sort_values(['IGM'],ascending=False )['nome'].tolist()    
    list_incadores_cluster = []
    for i in INDICADORES:
        list_cluster = gpd_municipios[gpd_municipios['Cluster'] == cluster].sort_values([i],ascending=False )['nome'].tolist()
        list_cluster = dict(zip(list_cluster,range(1,len(list_cluster)+1)))
        list_incadores_cluster.append(list_cluster)
    return cluster, list_incadores_cluster
    
def get_info(feature=None, color_prop="IGM"):
    header = [html.H4(f"{color_prop} - {ANO}")]
    if not feature:
        return header + [html.P("Passa o mouse sobre um município")]
    return header + [html.B(feature["properties"]["nome"]), html.Br(),
                     "{:.3f}".format(feature["properties"][color_prop])]
info = html.Div(children=get_info(), id="info", className="info",
                style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"})


def get_grafico_regiao(indicador,regiao,tipo_regiao):
    
    if not tipo_regiao =="Todos":
        df_result = df_tocantins[df_tocantins[tipo_regiao] == regiao]
    else:
        df_result = df_tocantins
# calula a média dos indicadores por ano
    df_result = df_result.groupby(['ano']).mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['IGM'],
                        mode='lines+markers',
                        name='IGM'))
    fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['Desempenho'],
                        mode='lines+markers',
                        name='Desempenho'))
    fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['Finanças'],
                        mode='lines+markers', name='Finanças'))
    
    fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['Gestão'],
                        mode='lines+markers', name='Gestão'))
    if tipo_regiao == "Todos":
        fig.update_layout(title=f'Indicadores do Tocantins',
                   xaxis_title='Ano',
                   yaxis_title='Valor do indicador')
    else:    
        fig.update_layout(title=f'Indicadores da região {regiao}',
                   xaxis_title='Ano',
                   yaxis_title='Valor do indicador')
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.4, y=-0.2,
                              xanchor='left', yanchor='top',
                              text='Fonte: https://igm.cfa.org.br/',
                              font=dict(family='Arial',
                                        size=12,
                                        color='rgb(150,150,150)'),
                              showarrow=False))

    fig.update_layout(annotations=annotations)

    #fig = px.line(df_result, x="ano", y=color_prop, markers=True, title=f'Índice {color_prop} - {df_result[7"nome"].iloc[0]}')        
    layout_result = html.Div([
            dcc.Graph(figure=fig, id="graph_regiao"),            
            ], className="w-100")
    return html.Div([layout_result],id="div_graph_regiao", className="container shadow  bg-body rounded d-flex ")

def get_grafico_municipio(value, color_prop="IGM"):
    df_result = df_tocantins[df_tocantins['nome'] == value]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['IGM'],
                        mode='lines+markers',
                        name='IGM'))
    fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['Desempenho'],
                        mode='lines+markers',
                        name='Desempenho'))
    fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['Finanças'],
                        mode='lines+markers', name='Finanças'))
    
    fig.add_trace(go.Scatter(x=df_result['ano'], y=df_result['Gestão'],
                        mode='lines+markers', name='Gestão'))
    fig.update_layout(title=f'Indicadores de {value}',
                   xaxis_title='Ano',
                   yaxis_title='Valor do indicador')
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.4, y=-0.2,
                              xanchor='left', yanchor='top',
                              text='Fonte: https://igm.cfa.org.br/',
                              font=dict(family='Arial',
                                        size=12,
                                        color='rgb(150,150,150)'),
                              showarrow=False))

    fig.update_layout(annotations=annotations)

    #fig = px.line(df_result, x="ano", y=color_prop, markers=True, title=f'Índice {color_prop} - {df_result[7"nome"].iloc[0]}')        
    layout_result = html.Div([
            dcc.Graph(figure=fig, id="graph"),            
            ], className="w-100")
    return html.Div([layout_result], className="container shadow  bg-body rounded d-flex ")

def get_indicadores_municipios(indicador_municipio,posicao_geral, list_rank_indicadores,grupo, nome_municipio  ):
    result_indicadores = []
    for indice in range(1,len(INDICADORES)):
        result_indicadores.append( html.Div(
                                                [
                                                    html.Hr(),
                                                    html.H6(f"{INDICADORES[indice]} :{indicador_municipio[indice]}",className="card-subtitle mb-2 text-muted"),
                                                    html.Div([
                                                        html.Div([
                                                            html.H6(f"Posição no ranking TO : {posicao_geral[indice][nome_municipio]}º ",), 
                                                            html.H6(f"Posição no {grupo} : {list_rank_indicadores[indice][nome_municipio]}º "), 
                                                            ] ),
                                                    ] , className="d-flex justify-content-between  container"),
                                                ],id="list_rank_indicadores" ))
    return result_indicadores

def get_dados_municipio(value, color_prop="IGM"):
    df_result = df_tocantins[df_tocantins['nome'] == value]
    nome_municipio  = value
    indicador_municipio  = [df_result[indicador].iloc[0] for indicador in INDICADORES]
    populacao_municipio  = df_result["População"].iloc[0]
    populacao_municipio = babel.numbers.format_number(populacao_municipio, locale='pt_BR')
    pib_municipio  = df_result["Pib per capita"].iloc[0]
    pib_municipio = babel.numbers.format_currency(pib_municipio, 'BRL', locale='pt_BR')
    posicao_geral = get_ranking_geral()
    grupo, list_rank_indicadores = ranking_municipio_grupo(nome_municipio)   
    layout_result =  html.Div(id = "dados_municipio_detalhe", children=[
                                
                                    html.Div(
                                        [html.H5(f"{nome_municipio}",className="card-title"),
                                        html.H6(f"{INDICADORES[0]} :{indicador_municipio[0]}",className="card-subtitle mb-2 text-muted"),
                                        html.Div([
                                            html.Div([
                                                html.H6(f"Posição no ranking TO : {posicao_geral[0][nome_municipio]}º ",id="",className=""), 
                                                html.H6(f"Posição no {grupo} : {list_rank_indicadores[0][nome_municipio]}º ",id="",className=""), 
                                            ]), 
                                            html.Div([
                                                html.H6(f"PIB : {pib_municipio}  ",id="",className=""), 
                                                html.H6(f"População : {populacao_municipio} Hab.",id="",className=""), 
                                            ]),
                                        ], className="d-flex justify-content-between container"),
                                       ]),
                                      
                                            *get_indicadores_municipios(indicador_municipio,posicao_geral, list_rank_indicadores,grupo, nome_municipio),
                                            
                                ],
                                
                                className="container d-grid", style={ 'height':'395px','overflowY': 'scroll'})
    
    return html.Div([layout_result],id="lista_idicadores", className="container shadow  bg-body rounded d-flex mt-1 ")

layout = html.Div(children=[
    html.Div( 
             html.Div([
                        html.Div([ 
                            html.Div([ 
                                    html.Div([     
                                        html.Label("Indicador:"),    
                                        dcc.Dropdown(
                                                            id='select_indicador',
                                                            options=['IGM', 'Finanças','Gestão','Desempenho'],
                                                            multi=False,
                                                            value='IGM',
                                                        ),
                                         html.Label("Tipo Região:"),                 
                                         dcc.RadioItems(
                                        [{ "label": html.Div(
                                                    [
                                                        html.Div("Todos", style={'fontSize': 15, 'paddingLeft': 3}),
                                                    ], style={'display': 'inline-block', 'alignItems': 'center', 'justifyContent': 'center'}
                                                ),
                                                "value": "Todos",
                                            },
                                    
                                         {"label": html.Div(
                                                    [
                                                        html.Div("Intermediária", style={'fontSize': 15, 'paddingLeft': 3}),
                                                    ], style={'display': 'inline-block', 'alignItems': 'center', 'justifyContent': 'center'}
                                                ),
                                                "value": "Intermediária",
                                            },
                                         {"label": html.Div(
                                                    [
                                                        html.Div("Imediata", style={'fontSize': 15, 'paddingLeft': 3}),
                                                    ], style={'display': 'inline-block', 'alignItems': 'center', 'justifyContent': 'center'}
                                                ),
                                                "value": "Imediata",
                                            },
                                         ],
                                         
                                         id = 'radio_tipo_regiao',  value='Todos', style = {'border':'1px solid #ccc', 'borderRadius':'5px', 'padding':'1px', 'margin':'5px'}, labelStyle={'padding':'5px' }, inline=True),
                                    ], className=""), 

                                    html.Label("Região:"),    
                                        dcc.Dropdown(
                                                            id='select_regiao',
                                                            options=['IGM', 'Finanças','Gestão','Desempenho'],
                                                            multi=False,
                                                            
                                                        ),

                                ], id="dropdown_indicador",className='p-3 mb-3 container  bg-body rounded d-flex flex-column'),
                                    
                                html.Div([get_map("IGM", geojson_municipios)],id='layout_map', className="container" ),            
                                ], className=" d-flex flex-column w-100"), 
                            html.Div([                             
                                html.Div([
                                           html.Div([      
                                           html.Label("Município:"),    
                                           dcc.Dropdown(
                                                            id='select_municipio',
                                                            options=gpd_municipios['nome'].unique().tolist(),
                                                            multi=False,
                                                            value='',
                                                        ),
                                                ], className="w-100"), 
                                         ], id="dropdown_cidades", className="p-2 mb-2 container   bg-body rounded d-flex"),
                                html.Div(id="grafico_igm", className="container"),
                                html.Div(id="grafico_regiao", className="container"),
                                html.Div(id="dados_municipio", className="container", ),
                                
                            ], className=" d-flex flex-column w-100")     
                        ],
                         className="container shadow  bg-body rounded d-flex p-2 col-lg-12"),),

])


@callback(
    Output("layout_map", "children"), 
    Output("select_municipio", "options"),
    Output("grafico_regiao", "children"),

    [Input("select_indicador", "value"),
    Input("radio_tipo_regiao", "value"), 
    Input("select_regiao", "value"), 
    ],
    State("select_municipio", "value"),
    )
    
def map_indicador(indicador, tipo_regiao, regiao, municipios):
    print('Tipo regiao: ',tipo_regiao)
    print('regiao: ',regiao)
    print(municipios)
    #geojson_municipios_tmp = 
    if tipo_regiao == "Todos":
        return get_map(indicador,geojson_municipios),gpd_municipios['nome'].unique().tolist(), get_grafico_regiao(indicador,regiao,tipo_regiao)
                
    if tipo_regiao == "Intermediária":
        df_result = gpd_municipios[gpd_municipios['Intermediária'] == regiao ].copy()
        geojson_municipios_tmp = geojson.loads(df_result.to_json())
        if (regiao == None ) or (regiao not in gpd_municipios['Intermediária'].unique().tolist()):
            return get_map(indicador,geojson_municipios_tmp),df_result['nome'].unique().tolist(),html.Div()    
        if municipios == None:	
            return get_map(indicador,geojson_municipios_tmp),gpd_municipios['nome'].unique().tolist(), get_grafico_regiao(indicador,regiao,tipo_regiao)            
       
        return get_map(indicador,geojson_municipios_tmp),df_result['nome'].unique().tolist(),html.Div() 
    
    if tipo_regiao == "Imediata":
        df_result = gpd_municipios[gpd_municipios['Imediata'] == regiao ].copy()
        geojson_municipios_tmp = geojson.loads(df_result.to_json())
        if regiao == None:
            return get_map(indicador,geojson_municipios_tmp),df_result['nome'].unique().tolist(),html.Div()
        if municipios == None:
            return get_map(indicador,geojson_municipios_tmp),gpd_municipios['nome'].unique().tolist(), get_grafico_regiao(indicador,regiao,tipo_regiao)

        return get_map(indicador,geojson_municipios_tmp),df_result['nome'].unique().tolist(), html.Div()
        
        

@callback(
    Output("select_municipio", "value"), 
    [Input("cidades", "click_feature")])
def capital_click(feature):
    if feature is not None:
        return feature['properties']['nome']

@callback(Output("info", "children"),
              [Input("cidades", "hover_feature"), 
               Input("select_indicador", "value")],)
def info_hover(feature, color_prop="IGM"):
    return get_info(feature, color_prop)

@callback(
    Output("grafico_igm", "children"),
    Output("dados_municipio", "children"),
    [Input('select_municipio','value'),
    Input("select_indicador", "value")
           ] ,
  
)
def update_output_div(input_value, color_prop="IGM",):
 
   
    if input_value is not None:
        return get_grafico_municipio(input_value,color_prop), get_dados_municipio(input_value, color_prop)
    else:
        return "", ""

@callback(
    Output("select_regiao", "options"),
    [Input("radio_tipo_regiao", "value")],
    )
def update_regiao(input_value):
    if input_value == "Todos":
        
        return [{'label': 'Todas', 'value': 'Todas'}]
    if input_value == "Intermediária":
        return gpd_municipios['Intermediária'].unique().tolist()
    if input_value == "Imediata":
        return gpd_municipios['Imediata'].unique().tolist()



