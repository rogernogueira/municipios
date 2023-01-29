import pandas as pd
import numpy as np
import geojson
import seaborn as sns
import geopandas as gpd
from libpysal.weights import Queen, Rook, KNN, spatial_lag
from splot import esda as esdaplot
import esda
from splot.esda import plot_moran, moran_scatterplot, lisa_cluster, plot_local_autocorrelation
import matplotlib.pyplot as plt
indicadores = ["IGM", "Desempenho", "Gestão", "Finanças"]
color_prop = 'IGM'
df_tocantins = pd.read_pickle('data/tocantins.pkl')
df_tocantins_ano = df_tocantins[df_tocantins['ano'] == 2021]
# df_tocantins_ano = df_tocantins

df_cidade_ibge = pd.read_json('data\\cidades.json')
df_cidade_to = df_cidade_ibge[df_cidade_ibge['codigo_uf']==17]

df_cidade_to = df_cidade_to.merge(df_tocantins_ano, left_on='codigo_ibge', right_on='Código IBGE')
dict_cidade_to = df_cidade_to.to_dict('records') 



for item in dict_cidade_to:
        item["tooltip"] = f"{item['nome_x']} - {item[color_prop]} IGM/CFA "
with open('assets\\to_municipios.json', encoding='utf-8') as f:
    geojson_municipios = geojson.load(f)

for feature in geojson_municipios['features']:
    for item in dict_cidade_to:
        if feature['properties']['id'] == str(item['codigo_ibge']):
            feature['properties']['tooltip'] = item['tooltip']
            feature['properties'][color_prop] = item[color_prop]
            feature['properties']['Cluster'] = item['Cluster']
            feature['properties']['Desempenho'] = item['Desempenho']
            feature['properties']['Gestão'] = item['Gestão']
            feature['properties']['Finanças'] = item['Finanças']
geojson.dump(geojson_municipios, open('data\\geo_municipios.json', 'w'))
df_geo = gpd.GeoDataFrame.from_features(geojson_municipios['features'])
df_geo.set_index('name', inplace=True)	
df_geo['corte'] = df_geo["IGM"].apply(lambda x: 1 if (x>5) else 0)
df_geo.to_json('data\\df_geo.json', driver='GeoJSON')
#11df_geo = df_geo[df_geo['Cluster'] == 'Grupo 1']
w_queen = Queen.from_dataframe(df_geo)

#lista de ilhas
list_islands = [df_geo.iloc[x].name for x in w_queen.islands] 
# Retirando as ilhas
df_geo.drop(list_islands, inplace=True)

        
w_queen = Queen.from_dataframe(df_geo)

ax = df_geo.plot(edgecolor='grey', facecolor='w')
f,ax = w_queen.plot(df_geo, ax=ax, 
        edge_kws=dict(color='r', linestyle=':', linewidth=1),
        node_kws=dict(marker=''))
ax.set_axis_off()


# todo o estado 
for i in indicadores:
    moran = esda.moran.Moran(df_geo[i], w_queen)
    print(f'=========={i}=======')
    print ('I global de moran: ', moran.I)
    print('p-value: ', moran.p_sim)
    if moran.p_sim< 0.005:
        print('Significante')
    else:
        print('Não Significante')
    print('=====================')
    
    lisa = esda.moran.Moran_Local(df_geo[color_prop], w_queen)
# grupos de cidades 
for grupo in df_geo['Cluster'].unique():
    try:
        w_queen = Queen.from_dataframe(df_geo[df_geo['Cluster']==grupo])        
            #lista de ilhas
        if len(w_queen.islands)>0:
            list_islands = [df_geo.iloc[x].name for x in w_queen.islands] 
            # Retirando as ilhas
            df_geo.drop(list_islands, inplace=True)
            list_islands =[] 
            w_queen = Queen.from_dataframe(df_geo[df_geo['Cluster']==grupo])
        moran = esda.moran.Moran(df_geo[df_geo['Cluster']==grupo][i], w_queen)
        for i in indicadores:
        
            print(f'========== {grupo} - {i}=======')
            print ('I global de moran: ', moran.I)
            print('p-value: ', moran.p_sim)
            if moran.p_sim< 0.005:
                print('Significante')
            else:
                print('Não Significante')
            print('=====================')
            
            lisa = esda.moran.Moran_Local(df_geo[df_geo['Cluster']==grupo][i], w_queen)
            plot_autocorrelation(lisa, df_geo[df_geo['Cluster']==grupo], i, grupo)
    except:
        print(f'Erro {grupo} - {i}')
        
plt.axvline(moran.I, color='k', linestyle='dashed', linewidth=1)
#plt.hist(moran.sim) 
plt.text(0.05,80, 'I de moran real: {:.4f}'.format(moran.I))
sns.histplot(moran.sim, kde=True)
                         
plot_moran(moran, zstandard=True, figsize=(7, 7))
lisa_cluster(lisa, df_geo, p=0.05, figsize=(7, 7))

moran_scatterplot(lisa, p=0.05)
plot_local_autocorrelation(lisa, df_geo,color_prop)


ax = sns.kdeplot(lisa.Is)
# Add one small bar (rug) for each observation
# along horizontal axis
sns.rugplot(lisa.Is, ax=ax)
labels = pd.Series(
    1 * (lisa.p_sim < 0.05),  # Assign 1 if significant, 0 otherwise
    index=df_geo.index  # Use the index in the original data
    # Recode 1 to "Significant and 0 to "Non-significant"
).map({1: "Significant", 0: "Non-Significant"})

df_geo["w_igm"] = spatial_lag.lag_spatial(
    w_queen, df_geo[color_prop]
)
df_geo["igm_std"] = df_geo[color_prop] - df_geo[color_prop].mean()
df_geo["w_igm_std"] = df_geo["w_igm"] - df_geo["w_igm"].mean()

# Setup the figure and axis
f, ax = plt.subplots(1, figsize=(6, 6))
# Plot values
sns.regplot(
    x="igm_std", y="w_igm_std", data=df_geo, ci=None
);

def plot_autocorrelation(lisa, df_geo, color_prop, grupo):
    # Set up figure and axes
    f, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 12))
    # Make the axes accessible with single indexing
   
    axs = axs.flatten()
    f.suptitle(f"Moran's I: {color_prop} - {grupo}", fontsize=20)

    # Subplot 1 #
    # Choropleth of local statistics
    # Grab first axis in the figure
    ax = axs[0]
    # Assign new column with local statistics on-the-fly
    df_geo.assign(
        Is=lisa.Is
        # Plot choropleth of local statistics
    ).plot(
        column="Is",
        cmap="plasma",
        scheme="quantiles",
        k=5,
        edgecolor="white",
        linewidth=0.1,
        alpha=0.75,
        legend=True,
        ax=ax,
    )

    # Subplot 2 #
    # Quadrant categories
    # Grab second axis of local statistics
    ax = axs[1]
    # Plot Quandrant colors (note to ensure all polygons are assigned a
    # quadrant, we "trick" the function by setting significance level to
    # 1 so all observations are treated as "significant" and thus assigned
    # a quadrant color
    esdaplot.lisa_cluster(lisa, df_geo, p=1, ax=ax)

    # Subplot 3 #
    # Significance map
    # Grab third axis of local statistics
    ax = axs[2]
    #
    # Find out significant observations
    labels = pd.Series(
        1 * (lisa.p_sim < 0.05),  # Assign 1 if significant, 0 otherwise
        index=df_geo.index  # Use the index in the original data
        # Recode 1 to "Significant and 0 to "Non-significant"
    ).map({1: "Significant", 0: "Non-Significant"})
    # Assign labels to `db` on the fly
    df_geo.assign(
        cl=labels
        # Plot choropleth of (non-)significant areas
    ).plot(
        column="cl",
        categorical=True,
        k=2,
        cmap="Paired",
        linewidth=0.1,
        edgecolor="white",
        legend=True,
        ax=ax,
    )


    # Subplot 4 #
    # Cluster map
    # Grab second axis of local statistics
    ax = axs[3]
    # Plot Quandrant colors In this case, we use a 5% significance
    # level to select polygons as part of statistically significant
    # clusters
    esdaplot.lisa_cluster(lisa, df_geo, p=0.05, ax=ax).

    # Figure styling #
    # Set title to each subplot
    for i, ax in enumerate(axs.flatten()):
        ax.set_axis_off()
        ax.set_title(
            [
                f"Local Statistics {grupo} - {color_prop}",
                f"Scatterplot Quadrant",
                f"Statistical Significance",
                f"Moran Cluster Map",
            ][i],
            y=0,
        )
    # Tight layout to minimise in-betwee white space
    f.tight_layout()

    # Display the figure
    plt.show()