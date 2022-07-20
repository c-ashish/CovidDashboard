import urllib
import json
import pandas as pd
from geopy.geocoders import Nominatim
import plotly.express as px
import folium
import altair as alt


def get_data_as_df_from_url(url, normalising_key, convert_to_datetime=True):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    df = pd.json_normalize(data, normalising_key)
    if convert_to_datetime:
        df["date"] = pd.to_datetime(df[['year', 'month', 'day']])

    return df


def get_country_names(df, country_name_column):
    country_names = df[country_name_column].unique()

    return country_names


def get_country_coordinates(country_names, geolocator_object):
    country_coordinates = dict()
    for country in country_names:
        location = geolocator_object.geocode(country)
        coordinates = [location.latitude, location.longitude]
        country_coordinates[country] = coordinates

    return country_coordinates


def plot_for_one_country(df, country_name, kpi):
    df_country = df[df.countriesAndTerritories == country_name]
    plot = alt.Chart(df_country, title=country_name).mark_line().encode(
            alt.X('date', scale=alt.Scale(zero=False)),
            alt.Y(kpi, scale=alt.Scale(zero=False)),
        )
    return plot


def plot_for_all_countries(df, countries, kpi, allow_output_mutation=True):
    dict_of_plots = dict()
    for country in countries:
        plot = plot_for_one_country(df, country, kpi)
        dict_of_plots[country] = plot
    return dict_of_plots


def create_map(country_coordinates, dict_of_plots, kpi):
    europe_map = folium.Map(location=[54, 15], zoom_start=3.2, tiles='cartodbpositron')
    for key, value in country_coordinates.items():
        country_plot = dict_of_plots[key]
        folium.vector_layers.CircleMarker(
            location=value,
            color="red",
            fill_opacity=0.7,
            radius=5,
            popup=folium.Popup().add_child(
                folium.features.VegaLite(country_plot)
            )
        ).add_to(europe_map)



