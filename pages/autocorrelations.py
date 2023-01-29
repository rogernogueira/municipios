import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import html, dcc, callback, Input, Output
import geopandas as gpd
from dash_extensions.javascript import assign,arrow_function
from libpysal.weights import Queen
import esda
import geojson
import pandas as pd

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css']
chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js" 
colorscale = [ '#304d63','#ED8975', '#8fb9aa', '#FD8D3C', ]
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7) 
dash.register_page(__name__)
with open('data\\geo_municipios.json', encoding='utf-8') as f:
    geojson_municipios = geojson.load(f)
df = gpd.GeoDataFrame.from_features(geojson_municipios['features'])
df.set_index('name', inplace=True)	


def get_info(feature=None, color_prop="IGM"):
    header = [html.H4(f"{color_prop} - 2021")]
    if not feature:
        return header + [html.P("Passa o mouse sobre um município")]
    return header + [html.B(feature["properties"]["name"]), html.Br(),
                     "{:.3f}".format(feature["properties"][color_prop])]
    
info = html.Div(children=get_info(), id="info_sig", className="info",
                 style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000"})

style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    console.log('valor',value);
    if (value > 0) {
        style.fillColor = colorscale[1];  // set the fill color according to the class
    }else{
        style.fillColor = colorscale[0];
    };

  
    return style;
}""")





def get_map_sig(df, color_prop, grupo):
    classes=[0,1]
    ctg = ['Não Significante', 'Significante' ]
    colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, unit='IGM', position='bottomleft')
    if grupo == 'Todos':
        df_geo = df.copy()
    else:
        df_geo = df[df['Cluster']==grupo].copy()
    # w_queen
    w_queen = Queen.from_dataframe(df_geo)        
        #lista de ilhas
    if len(w_queen.islands)>0:
        list_islands = [df_geo.iloc[x].name for x in w_queen.islands] 
        # Retirando as ilhas
        df_geo.drop(list_islands, inplace=True )
        list_islands =[] 
        w_queen = Queen.from_dataframe(df_geo)
    moran = esda.moran.Moran(df_geo[color_prop], w_queen)
    lisa = esda.moran.Moran_Local(df_geo[color_prop], w_queen)
    
    labels = pd.Series(
    1 * (lisa.p_sim < 0.05),  # Assign 1 if significant, 0 otherwise
    index=df_geo.index
    )# Use the index in the original data
    df_geo['p-value'] = labels# Recode 1 to "Significant and 0 to "Non-significant"
    geojson_municipios_filter = df_geo.to_json()
   

    return     dl.Map(center=[-9.407668341753798, -48.416790644617116], zoom=7, children=[
                                        dl.TileLayer(),
                                        dl.GeoJSON(data =geojson_municipios_filter, format="geojson", id="cidades",
                                                    options=dict(style=style_handle),
                                                    zoomToBounds=True,
                                                    zoomToBoundsOnClick=False,
                                                    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
                                                    hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp='p-value'),
                                                ),  
                                        colorbar, 
                                        info,  
                                        # geobuf resource (fastest option)
                                    ], style={'width': '100%', 'height': '90vh', 'margin': "auto", "display": "block"}, id="map_sig")



layout = html.Div(children=[
    
             html.Div([
                        html.Div([      
                                    html.Label("Indicador:"),    
                                    dcc.Dropdown(
                                                        id='select_indicador_significancia',
                                                        options=['IGM', 'Finanças','Gestão','Desempenho'],
                                                        multi=False,
                                                        value='IGM',
                                                    ),
                                    dcc.Dropdown(
                                                        id='select_grupo_significancia',
                                                        options=['Grupo 1', 'Grupo 2','Todos',],
                                                        multi=False,
                                                        value='Todos',
                                                    ),
                                    html.Div([get_map_sig(df, "IGM", "Todos")],id='layout_map_sig' ),            
                                ], id="dropdown_indicador",className='container shadow'),
                                                             
],)
             
])


@callback(
    Output(component_id="layout_map_sig", component_property='children'),
    Input('select_indicador_significancia','value')
)
def update_city_selected_sig(value):
    return get_map_sig(df,value, 'Todos')

@callback(Output("info_sig", "children"),
               [Input("cidades", "hover_feature"), 
                Input("select_indicador", "value")],)
def info_hover_sig(feature, color_prop="IGM"):
     return get_info(feature, color_prop)