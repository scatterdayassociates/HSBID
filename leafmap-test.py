import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import geopandas as gpd

# Set page configuration
st.set_page_config(
    page_title="Scatterday & Associates Mapping Visualization Demo",
    layout="wide"
)

# Add title and description
st.title("Scatterday & Associates Mapping Visualization Demo")
st.markdown("A simple demonstration of integrating leafmap with Streamlit for geospatial visualization")

# Create a sample dataframe with lat/lon coordinates
data = {
    'lat': [37.76, 34.05, 40.71, 51.51, 48.85],
    'lon': [-122.4, -118.25, -74.01, -0.12, 2.35],
    'name': ['San Francisco', 'Los Angeles', 'New York', 'London', 'Paris'],
    'value': [10, 20, 15, 25, 30]
}
df = pd.DataFrame(data)

# Convert to GeoDataFrame
import geopandas as gpd
gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df['lon'], df['lat']),
    crs='epsg:4326'
)

# Create a map
m = leafmap.Map(center=[40, -100], zoom=3, toolbar_control=True, layers_control=True)

# Add the GeoDataFrame to the map
m.add_gdf(gdf, layer_name="Cities")

# Add different basemap options
m.add_basemap("OpenStreetMap")
m.add_basemap("Stamen.Terrain")

# Create sidebar with options
with st.sidebar:
    st.header("Map Controls")
    
    # Add a basemap selector
    basemap = st.selectbox(
        "Select Basemap",
        ["OpenStreetMap", "SATELLITE", "Stamen.Terrain"]
    )
    
    # Add a checkbox for split view
    split_view = st.checkbox("Enable Split View")

# Apply selected basemap
if basemap:
    m.add_basemap(basemap)

# Apply split view if selected
if split_view:
    m.split_map(
        left_layer="OpenStreetMap",
        right_layer="SATELLITE"
    )

# Display the map in Streamlit
m.to_streamlit(height=600)

# Add some additional information below the map
st.subheader("Dataset Information")
st.dataframe(df)

# Add a simple chart
st.subheader("Value by City")
st.bar_chart(df.set_index('name')['value'])
