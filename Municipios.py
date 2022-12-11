import pandas as pd
import json
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, Output, Input
from dash_extensions.javascript import arrow_function
from dash_extensions.javascript import assign, Namespace
import geojson

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css']
chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js" 
colorscale = ['#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
color_prop = 'IGM/CFA'
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

df_tocantins = pd.read_pickle('data\\tocantins.pkl')
# ano de 2021
df_tocantins = df_tocantins[df_tocantins['ano'] == 2021][["Código IBGE","IGM/CFA"]]	

df_cidade_ibge = pd.read_json('data\\cidades.json')
df_cidade_to = df_cidade_ibge[df_cidade_ibge['codigo_uf']==17]
df_cidade_to = df_cidade_to.merge(df_tocantins, left_on='codigo_ibge', right_on='Código IBGE')
dict_cidade_to = df_cidade_to.to_dict('records') 
for item in dict_cidade_to:
        item["tooltip"] = f"{item['nome']} - {item[color_prop]} IGM/CFA "
min = df_cidade_to[color_prop].min()    
max = df_cidade_to[color_prop].max()

with open('assets\\to_municipios.json', encoding='utf-8') as f:
    geojson_municipios = geojson.load(f)

for feature in geojson_municipios['features']:
    for item in dict_cidade_to:
        if feature['properties']['id'] == str(item['codigo_ibge']):
            feature['properties']['tooltip'] = item['tooltip']
            feature['properties'][color_prop] = item[color_prop]
 
#colorbar = dl.Colorbar(colorscale=colorscale, width=20, height=150, min=min, max=max, unit=' IGM/CFA')

classes = df_cidade_to[color_prop].quantile([0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]).tolist()    
ctg = ["{}".format(cls, classes[i + 1])[:3] for i, cls in enumerate(classes[:-1])] + ["{}".format(classes[-1])[:3]]
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, unit='IGM/CFA', position='bottomleft')

geojson_ibge = dlx.dicts_to_geojson(dict_cidade_to, lon="longitude", lat="latitude")  # convert to geojson
geobuf_ibge = dlx.geojson_to_geobuf(geojson_ibge)


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
    
#cidades_json = json.loads('data\\to_municipios.json')
point_to_layer = assign("""function(feature, latlng, context){
    const {min, max, colorscale, circleOptions, colorProp} = context.props.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
    circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop.
    return L.circleMarker(latlng, circleOptions);  // sender a simple circle marker.
}""")

def get_info(feature=None):
    header = [html.H4("IGM/CFA - 2021")]
    if not feature:
        return header + [html.P("Passa o mouse sobre um município")]
    return header + [html.B(feature["properties"]["name"]), html.Br(),
                     "{:.3f}".format(feature["properties"][color_prop])]
info = html.Div(children=get_info(), id="info", className="info",
                style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000"})
app = Dash( suppress_callback_exceptions=True, external_stylesheets=external_stylesheets, external_scripts=[chroma], prevent_initial_callbacks=True)
app.layout = html.Div([
                        html.Div([
                            html.Div([       
                                dl.Map(center=[-9.407668341753798, -48.416790644617116], zoom=7, children=[
                                        dl.TileLayer(),
                                        dl.GeoJSON(data =geojson_municipios, format="geojson", id="cidades",
                                                    options=dict(style=style_handle),
                                                    zoomToBounds=True,
                                                    zoomToBoundsOnClick=True,
                                                    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),
                                                    hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp=color_prop),
                                                ),  
                                        colorbar, 
                                        info,  
                                        # geobuf resource (fastest option)
                                    ], style={'width': '100%', 'height': '90vh', 'margin': "auto", "display": "block"}, id="map"),
                            ], className='container '),
                             html.Div(id="state", className="container"),
                             html.Div(id="capital", className="container"),    
                       
                        ],
                                
                         className="container shadow  bg-body rounded row "),
                        
                        
])

@app.callback(
    Output("capital", "children"), 
    [Input("cidades", "click_feature")])
def capital_click(feature):
    if feature is not None:
        return html.Div(f"You clicked {feature['properties']['id']}")

@app.callback(Output("info", "children"), [Input("cidades", "hover_feature")])
def info_hover(feature):
    return get_info(feature)

if __name__ == '__main__':
    app.run_server()