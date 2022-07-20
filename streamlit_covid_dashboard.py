import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium
import constants
import helper_functions
from geopy.geocoders import Nominatim


st.header("Covid-19 Dashboard")
st.write("""
The dashboard gives you information about statistics and visualizations on the number of cases and number of deaths due
to Covid-19.
""")

df = helper_functions.get_data_as_df_from_url(
    url='https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/json/',
    normalising_key='records',
    convert_to_datetime=True
)
country_names = helper_functions.get_country_names(
    df=df,
    country_name_column='countriesAndTerritories'
)
geolocator=Nominatim(user_agent="https://c-ashish-coviddashboard-streamlit-covid-dashboard-qm32ap.streamlitapp.com/")
country_coordinates = helper_functions.get_country_coordinates(
    country_names=country_names,
    geolocator_object=geolocator
)

st.header("Map")
st.write("""
The map is interactive, you may click on the displayed country names to get an overview about the Coivd-19 related
summary.
""")

kpi_for_map = st.selectbox('Covid-19 KPI for Map',
                           options=list(constants.MAP_KPIS.keys()),
                           index=0,
                           format_func=lambda kpi: constants.MAP_KPIS[kpi])
dict_of_plots = helper_functions.plot_for_all_countries(df=df,
                                                        countries=country_names,
                                                        kpi=kpi_for_map)
eu_map = helper_functions.create_map(country_coordinates=country_coordinates,
                                     dict_of_plots=dict_of_plots,
                                     kpi=kpi_for_map)
folium_static(eu_map)

st.write("Map was displayed")
# Make an empty map
europe_map = folium.Map(location=[54, 15], zoom_start=3.2, tiles='cartodbpositron')
folium_static(europe_map)
