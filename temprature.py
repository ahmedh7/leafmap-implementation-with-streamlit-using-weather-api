import streamlit as st
import geopandas as gpd
import leafmap.foliumap as lm
import requests
import pandas as pd

map = lm.Map(max_zoom=7)

api_key = "8a07d886a504428a8e1202226231003"
base_url = "http://api.weatherapi.com/v1/current.json?key=" + api_key + "&q="
forecast_url = "http://api.weatherapi.com/v1/future.json?key=" + api_key + "&q=&dt=2023-04-09"

def get_current_temperature(city):
    url = base_url + city
    response = requests.get(url)
    weather_data = response.json()

    country = weather_data["location"]["country"]
    lat = weather_data["location"]["lat"]
    lon = weather_data["location"]["lon"]
    localtime = weather_data["location"]["localtime"]
    temp = weather_data["current"]["temp_c"]
    text = weather_data["current"]["condition"]["text"]
    humidity = weather_data["current"]["humidity"]
    pressure_mb = weather_data["current"]["pressure_mb"]
    map.set_center(lon,lat)

    df = pd.DataFrame({
        "Country": [country],
        "Temperature (°C)": [temp],
        "Humidity (%)": [humidity],
        "Pressure (mb)": [pressure_mb],
        "Weather Condition": [text],
        "Local Time": [localtime],
        "Latitude": [lat],
        "Longitude": [lon],
    })
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    gdf = gdf.set_crs("EPSG:4326")
    map.add_gdf(gdf,layer_name="City Pin",zoom_to_layer=False)
    
def addAttributesOptions(gfile):
    atts = gfile.columns
    tuAtts = tuple(atts)
    attList = st.selectbox("Choose the value column",tuAtts[2:])
    if not attList == " ":
        lat = gfile.geometry.y
        long = gfile.geometry.x
        value = gfile[attList]
        length = len(lat)

        data = []
        for i in range(0,length):
            point = [lat[i],long[i],float(value[i])]
            data.append(point)
        map.add_heatmap(data)
with st.sidebar:
    st.markdown("<h1 style='color: black; text-align: center;'>Weather Map</h1>", unsafe_allow_html=True)
    st.write("""Type a city name and press Enter.
             Hover over the Pin to display weather data.""")
    baseList = st.selectbox("Choose your Basemap", ("Open Street Map", "Google HYBRID"))
    city = st.text_input("Enter a city name:")

    st.markdown("<h1 style='color: black; text-align: center;'>Heat Map</h1>", unsafe_allow_html=True)
    cities = st.file_uploader("Upload a GeoJSON file for the heatmap", type="geojson")
    if baseList == "Open Street Map":
        pass
    else:
        map.add_basemap("HYBRID") 

    if city:
        get_current_temperature(city)
    if cities:
        gfile = gpd.read_file(cities)
        heat_data = [[row["geometry"].y, row["geometry"].x, row["temprature"]] for index, row in gfile.iterrows()]
        addAttributesOptions(gfile)
        map.fit_bounds(map.get_bounds(), padding=(30, 30))


    

map.to_streamlit(height=500)

