import streamlit as st
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

import constants
import helper_functions


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
geolocator = Nominatim(user_agent="https://c-ashish-coviddashboard-streamlit-covid-dashboard-qm32ap.streamlitapp.com/")
country_coordinates = helper_functions.get_country_coordinates(
    country_names=country_names,
    geolocator_object=geolocator
)

st.header("Map")
st.write("""
The map is interactive, you may click on the displayed country names to get an overview about the Covid-19 related
summary.
""")

kpi_for_map = st.selectbox('Covid-19 KPI for Map',
                           options=list(constants.MAP_KPIS.keys()),
                           index=0,
                           format_func=lambda kpi: constants.MAP_KPIS[kpi])
dict_of_plots = helper_functions.plot_for_all_countries(df=df,
                                                        countries=country_names,
                                                        kpi=kpi_for_map)
df_last_week_sum = helper_functions.get_last_week_stats(df)
eu_map = helper_functions.create_map(country_coordinates=country_coordinates,
                                     dict_of_plots=dict_of_plots,
                                     df_last_week_sum=df_last_week_sum,
                                     kpi=kpi_for_map,
                                     df=df)
folium_static(eu_map)

st.header("Covid-19 statistics for EU Countries")
st.write("The maps are interactive and can be zoomed on.\n"
         "You May click on the legend to disable some plotted lines.\n"
         "You May select multiple countries for which you wish to see the statistics.")
countries_for_plot = st.multiselect('Select Countries',
                                    options=list(country_names),
                                    default=country_names[0])

plot = helper_functions.make_pivot_plots(df, countries_for_plot)
st.plotly_chart(plot)


