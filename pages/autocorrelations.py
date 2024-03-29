import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import html, dcc, callback, Input, Output, State
import geopandas as gpd
from dash_extensions.javascript import assign,arrow_function
from libpysal.weights import Queen
import esda
import geojson
import json
import pandas as pd
import configparser
import babel.numbers

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css']
chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js" 
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7) 
dash.register_page(__name__)

# with open('data/geo_municipios.json', encoding='utf-8') as f:
#     geojson_municipios = geojson.load(f)
# df = gpd.GeoDataFrame.from_features(geojson_municipios['features'])
# df.set_index('name', inplace=True)	

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
ANO = int(config['DEFAULT']['ANO'])
colorscale = config['DEFAULT']['COLORSCALE'].split(',')

df=gpd.GeoDataFrame.from_file('data/geo_municipios.json', driver="GeoJSON")


def get_info(feature=None):
    header = [html.H4(f"Índice de Moran - {ANO}")]
    if not feature:
        return header + [html.P("Passa o mouse sobre um município")]
    return header + [html.B(feature["properties"]["description"]), html.Br(),
                     "I moran: {:.3f}".format(feature["properties"]['Índice de Moran']),
                     html.Br(),
                     "P-value: {:.3f}".format(feature["properties"]['p-value']),
                     ]
    
info = html.Div(children=get_info(), id="info_sig", className="info",
                 style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"})
def get_info_cluster(feature=None, color_prop="IGM"):
    header = [html.H4(f"{color_prop} - {ANO}")]
    if not feature:
        return header + [html.P("Passa o mouse sobre um município")]
    if color_prop == "População":
        return header + [html.B(feature["properties"]["description"]), html.Br(),
                     "{}".format(babel.numbers.format_decimal(feature["properties"][color_prop], locale='pt_BR'))]
    return header + [html.B(feature["properties"]["description"]), html.Br(),
                     "{}".format(feature["properties"][color_prop])]
    
info_cluster = html.Div(children=get_info_cluster(), id="info_sig_cluster", className="info",
                 style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"})

style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from 
    const value = feature.properties[colorProp];  // get value the determines the color
    if (value > 0) {
        style.fillColor = colorscale[1];  // set the fill color according to the class
    }else{
        style.fillColor = colorscale[0];
    };
    return style;
}""")


style_handle_cluster = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    const quad = feature.properties['quadrantes'];  // get value the determines the color
    

    if (value > 0) {
        if (quad == 1){
            style.fillColor = colorscale[1];
        }
        else if (quad == 2){
            style.fillColor = colorscale[2];
        }
        else if (quad == 3){
            style.fillColor = colorscale[3];
        } else if (quad == 4){
            style.fillColor = colorscale[4];
        }        
    
    }else {
           style.fillColor = colorscale[0];
    };
    return style;
}""")




def get_map_sig(df, color_prop, grupo, tipo_grupo="Todos"):
    classes=[0,1]
    ctg = ['Não Significante', 'Significante' ]
    colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale[0:2], width=300, height=30, unit='IGM', position='bottomright')
    classes_cluster = [0,1,2,3,4]
    ctg_cluster = ['Não Significante', 'HH', 'LH','LL','HL']
    colorbar_cluster = dlx.categorical_colorbar(categories=ctg_cluster, colorscale=colorscale, height=30,width=300, unit='IGM', position='bottomright')

    if tipo_grupo == 'Todos':
        df_geo = df.copy()
    if tipo_grupo == 'CFA':
        df_geo = df[df['Cluster']==grupo].copy()
    if tipo_grupo == 'Mesorregião':
        df_geo = df[df['Mesorregião']==grupo].copy()
    if tipo_grupo == 'Microrregião':
        df_geo = df[df['Microrregião']==grupo].copy()
    if tipo_grupo == 'Intermediária':
        df_geo = df[df['Intermediária']==grupo].copy()
    if tipo_grupo == 'Imediata':
        df_geo = df[df['Imediata']==grupo].copy()
    # w_queen
    w_queen = Queen.from_dataframe(df_geo,silence_warnings=True)        
        #lista de ilhas
    if len(w_queen.islands)>0:
        list_islands = [df_geo.iloc[x].name for x in w_queen.islands] 
        # Retirando as ilhas
        df_geo.drop(list_islands, inplace=True )
        list_islands =[] 
        w_queen = Queen.from_dataframe(df_geo)
    w_queen.transform = 'r'
    moran = esda.moran.Moran(df_geo[color_prop], w_queen)
    lisa = esda.moran.Moran_Local(df_geo[color_prop].apply(lambda x : (x-df_geo[color_prop].mean())/df_geo[color_prop].std()), w_queen)
    
    imoran =lisa.Is
    labels = pd.Series(
    1 * (lisa.p_sim < 0.05),  # Assign 1 if significant, 0 otherwise
    index=df_geo.index
    )# Use the index in the original data
    quadrantes = pd.Series(lisa.q, index=df_geo.index)
    df_geo['Índice de Moran'] = pd.Series(imoran, index=df_geo.index)
    df_geo['Significancia'] = labels# Recode 1 to "Significant and 0 to "Non-significant"
    df_geo['quadrantes'] = quadrantes
    df_geo['p-value'] = pd.Series(lisa.p_sim, index=df_geo.index)
    
    geojson_municipios_filter = df_geo.to_json()
    geojson_municipios_filter = json.loads(geojson_municipios_filter)
   

    return  html.Div(children=[ 
            html.Div(children=[
              html.H5('Mapa de Significância Espacial'),  
              dl.Map(center=[-9.407668341753798, -48.416790644617116], zoom=7, children=[
                                        dl.TileLayer(),
                                        dl.GeoJSON(data =geojson_municipios_filter, format="geojson", id="cidades_sig",
                                                    options=dict(style=style_handle),
                                                    zoomToBounds=True,
                                                    zoomToBoundsOnClick=False,
                                                    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
                                                    hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp='Significancia'),
                                                ),  
                                        colorbar, 
                                        info,  
                                        # geobuf resource (fastest option)
                                    ], style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"}, id="map_sig"), 
            ], className='container shadow', style={'marginTop': '10px'}),
            html.Div(children=[    
              html.H5('Mapa de Clusters'),
              dl.Map(center=[-9.407668341753798, -48.416790644617116], zoom=7, children=[
                                        dl.TileLayer(),
                                        dl.GeoJSON(data =geojson_municipios_filter, format="geojson", id="cidades_sig_cluster",
                                                    options=dict(style=style_handle_cluster),
                                                    zoomToBounds=True,
                                                    zoomToBoundsOnClick=False,
                                                    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
                                                    hideout=dict(colorscale=colorscale, classes=classes_cluster, style=style, colorProp='Significancia'),
                                                    
                                                ),  
                                        colorbar_cluster, 
                                        info_cluster,  
                                        # geobuf resource (fastest option)
                                    ], style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"}, id="map_cluster"),  
                ], className='container shadow  ', style={'marginTop': '10px'}),
    ], className = "d-flex justify-content-end")


layout = html.Div(children=[
    
             html.Div([
                        html.Div([      
                                    html.Label("Indicador:"),    
                                    dcc.Dropdown(
                                                        id='select_indicador_significancia',
                                                        options=['IGM', 'Finanças','Gestão','Desempenho', 'População'],
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
                                         { "label": html.Div(
                                                    [
                                                        html.Div("CFA", style={'fontSize': 15, 'paddingLeft': 3}),
                                                    ], style={'display': 'inline-block', 'alignItems': 'center', 'justifyContent': 'center'}
                                                ),
                                                "value": "CFA",
                                            },
                                         { "label": html.Div(
                                                    [
                                                        html.Div("Mesorregião", style={'fontSize': 15, 'paddingLeft': 3}),
                                                    ], style={'display': 'inline-block', 'alignItems': 'center', 'justifyContent': 'center'}
                                                ),
                                                "value": "Mesorregião",
                                            },
                                         {"label": html.Div(
                                                    [
                                                        html.Div("Microrregião", style={'fontSize': 15, 'paddingLeft': 3}),
                                                    ], style={'display': 'inline-block', 'alignItems': 'center', 'justifyContent': 'center'}
                                                ),
                                                "value": "Microrregião",
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
                                            }
                                         ],
                                         id = 'radio_grupo_significancia',  value='Todos', style = {'border':'1px solid #ccc', 'borderRadius':'5px', 'padding':'1px', 'margin':'5px'}, labelStyle={'padding':'5px' }, inline=True), 
                                    html.Label("Região:"), 
                                    dcc.Dropdown(   
                                                        id='select_grupo_significancia',
                                                        options=['Todos'],
                                                        multi=False,
                                                        value='Todos',
                                                        className= 'dropdown',
                                                        style={
                                                                'position': 'relative',
                                                                'zIndex': '99999',
                                                            }, 
                                                    ),
                                    html.Div([get_map_sig(df, "IGM", "Todos")],id='layout_map_sig' ),            
                                ], id="dropdown_indicador",className='container shadow'),
                                                             
],)
            
])

@callback(Output('select_grupo_significancia', 'options'),
         Output('select_grupo_significancia', 'value'),
                [Input('radio_grupo_significancia', 'value')],
            )
def choice_group(value):
    if value == 'Todos':
        return ['Todos'], 'Todos' 
    elif value == 'CFA':
        return [{'label': 'Grupo 1 - CFA', 'value': 'Grupo 1'},{'label': 'Grupo 2 - CFA', 'value':'Grupo 2'}], 'Grupo 1'
    elif value == 'Mesorregião':
        return [{'label': i, 'value': i} for i in df['Mesorregião'].unique()],df['Mesorregião'].unique()[0] 
    elif value == 'Microrregião':
        return [{'label': i, 'value': i} for i in df['Microrregião'].unique()], df['Microrregião'].unique()[0]
    elif value == 'Intermediária':
        return [{'label': i, 'value': i} for i in df['Intermediária'].unique()], df['Intermediária'].unique()[0]
    elif value == 'Imediata':
        return [{'label': i, 'value': i} for i in df['Imediata'].unique()], df['Imediata'].unique()[0]
    return []

@callback(
    Output(component_id="layout_map_sig", component_property='children'),
    [Input('select_indicador_significancia','value'),
     Input('select_grupo_significancia','value'),],
    [State('radio_grupo_significancia', 'value')]
)
def update_city_selected_sig(value_indicador, value_grupo, value_radio):
    return get_map_sig(df,value_indicador, value_grupo, value_radio)

@callback(Output("info_sig", "children"),
               [Input("cidades_sig", "hover_feature"), 
                Input("select_indicador_significancia", "value")],)
def info_hover_sig(feature, color_prop="IGM"):
     return get_info(feature)



@callback(Output("info_sig_cluster", "children"),
               [Input("cidades_sig_cluster", "hover_feature"), 
                Input("select_indicador_significancia", "value")],)
def info_hover_sig(feature, color_prop="IGM"):
     return get_info_cluster(feature, color_prop)     