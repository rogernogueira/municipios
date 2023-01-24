import pandas as pd
import geojson
import seaborn
import geopandas as gpd
from libpysal.weights import Queen, Rook, KNN, spatial_lag
import esda
from splot.esda import plot_moran, moran_scatterplot, lisa_cluster, plot_local_autocorrelation
import matplotlib.pyplot as plt

color_prop = 'IGM/CFA'

df = pd.read_pickle('.\\data\\tocantins.pkl')
df_tocantins_ano = df[df['ano'] == 2021][['nome', "Código IBGE","IGM/CFA", 'Cluster']]

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
df_geo = gpd.GeoDataFrame.from_features(geojson_municipios['features'])
df_geo.set_index('name', inplace=True)	
df_geo['corte'] = df_geo["IGM/CFA"].apply(lambda x: 1 if (x>5) else 0)
#df_geo = df_geo[df_geo['Cluster'] == 'Grupo 1']
w_queen = Queen.from_dataframe(df_geo)

#lista de ilhas
list_islands = [df_geo.iloc[x].name for x in w_queen.islands] 
# Retirando as ilhas
df_geo.drop(list_islands, inplace=True)

        
w_queen = Queen.from_dataframe(df_geo)



lisa = esda.moran.Moran_Local(df_geo['corte'], w_queen)

moran = esda.moran.Moran(df_geo['corte'], w_queen)
plot_moran(moran, zstandard=False, figsize=(7, 7))
lisa_cluster(lisa, df_geo, p=0.05, figsize=(7, 7))

moran_scatterplot(lisa, p=0.05)
plot_local_autocorrelation(lisa, df_geo,'corte')


ax = seaborn.kdeplot(lisa.Is)
# Add one small bar (rug) for each observation
# along horizontal axis
seaborn.rugplot(lisa.Is, ax=ax)
labels = pd.Series(
    1 * (lisa.p_sim < 0.05),  # Assign 1 if significant, 0 otherwise
    index=df_geo.index  # Use the index in the original data
    # Recode 1 to "Significant and 0 to "Non-significant"
).map({1: "Significant", 0: "Non-Significant"})

df_geo["w_igm"] = spatial_lag.lag_spatial(
    w_queen, df_geo["corte"]
)
df_geo["igm_std"] = df_geo["corte"] - df_geo["corte"].mean()
df_geo["w_igm_std"] = df_geo["w_igm"] - df_geo["corte"].mean()

# Setup the figure and axis
f, ax = plt.subplots(1, figsize=(6, 6))
# Plot values
seaborn.regplot(
    x="igm_std", y="w_igm_std", data=df_geo, ci=None
);

from splot import esda as esdaplot
# Set up figure and axes
f, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 12))
# Make the axes accessible with single indexing
axs = axs.flatten()

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
esdaplot.lisa_cluster(lisa, df_geo, p=0.05, ax=ax)

# Figure styling #
# Set title to each subplot
for i, ax in enumerate(axs.flatten()):
    ax.set_axis_off()
    ax.set_title(
        [
            "Local Statistics",
            "Scatterplot Quadrant",
            "Statistical Significance",
            "Moran Cluster Map",
        ][i],
        y=0,
    )
# Tight layout to minimise in-betwee white space
f.tight_layout()

# Display the figure
plt.show()