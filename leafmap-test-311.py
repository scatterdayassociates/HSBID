import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import geopandas as gpd
import requests

# Set page configuration
st.set_page_config(
    page_title="Hudson Square BID 311 Complaint Mapping",
    layout="wide"
)

# Add title and description
st.title("Hudson Square BID 311 Complaint Mapping Visualization Demo")
st.markdown("A simple demonstration of 311 data visualization for BID member, community and government agency engagement")

# Fetch GeoJSON data from API URL
geojson_url = "https://data.cityofnewyork.us/resource/erm2-nwe9.geojson"
response = requests.get(geojson_url)

if response.status_code == 200:
    geojson_data = response.json()
    
    # Convert GeoJSON to DataFrame
    df = pd.json_normalize(geojson_data['features'])
    
    # Extract the specified variables
    variables = [
        "created_date", 
        "agency", 
        "complaint_type", 
        "descriptor", 
        "location_type", 
        "incident_address", 
        "community_board", 
        "open_data_channel_type"
    ]
    
    # Create a new DataFrame with the specified columns
    data_df = pd.DataFrame()
    for var in variables:
        if f'properties.{var}' in df.columns:
            data_df[var] = df[f'properties.{var}']
    
    # Extract coordinates from properties instead of geometry
    data_df['lon'] = df['properties.longitude']
    data_df['lat'] = df['properties.latitude']

    # Create GeoDataFrame with only valid coordinates
    valid_coords = data_df.dropna(subset=['lon', 'lat'])
    gdf = gpd.GeoDataFrame(
        valid_coords,  # Use valid_coords as the base DataFrame instead of data_df
        geometry=gpd.points_from_xy(valid_coords['lon'], valid_coords['lat']),
        crs='epsg:4326'
)

    


    # Create a map centered on New York City
    m = leafmap.Map(center=[40.7128, -74.0060], zoom=12, toolbar_control=True, layers_control=True)
    
    # Add the GeoDataFrame to the map
    m.add_gdf(gdf, layer_name="NYC 311 Complaints")
    
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
        
        # Add a dropdown for selecting variable for bar chart
        chart_variable = st.selectbox(
            "Select Variable for Bar Chart",
            variables
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
    m.to_streamlit(height=700)
    
    # Add some additional information below the map
    st.subheader("Dataset Information")
    st.dataframe(data_df)
    
    # Create a bar chart based on the selected variable
    st.subheader(f"Distribution of {chart_variable}")
    if not data_df.empty and chart_variable in data_df.columns:
        # Get value counts and sort by frequency
        value_counts = data_df[chart_variable].value_counts().head(10)
        st.bar_chart(value_counts)
        
        # Display a table of the top values
        st.subheader(f"Top 10 {chart_variable} Values")
        value_counts_df = pd.DataFrame({
            chart_variable: value_counts.index,
            'Count': value_counts.values
        })
        st.dataframe(value_counts_df)
    else:
        st.error(f"No data available for {chart_variable}")
else:
    st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
    st.write("Please check the API URL or try again later.")

