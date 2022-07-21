import urllib
import json

import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import folium
import altair as alt
import streamlit as st
from branca.colormap import linear, LinearColormap

import constants


#@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_data_as_df_from_url(url, normalising_key, convert_to_datetime=True):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    df = pd.json_normalize(data, normalising_key)
    if convert_to_datetime:
        df["date"] = pd.to_datetime(df[['year', 'month', 'day']])
    df = df.sort_values('date')

    return df


def get_country_names(df, country_name_column):
    country_names = df[country_name_column].unique()
    country_names = sorted(country_names)
    return country_names


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_country_coordinates(country_names, geolocator_object):
    country_coordinates = dict()
    for country in country_names:
        location = geolocator_object.geocode(country)
        coordinates = [location.latitude, location.longitude]
        country_coordinates[country] = coordinates

    return country_coordinates


def get_last_week_stats(df):
    df = df.sort_values('date')
    cut_off_date = df['date'].max() - pd.to_timedelta("7 days")
    df_last_week = df[df.date > cut_off_date]
    df_last_week_sum = df_last_week.groupby("countriesAndTerritories").sum()
    df_last_week_sum.drop(columns=['year'], inplace=True)
    total_weekly_cases = df_last_week_sum['cases'].sum()
    total_weekly_deaths = df_last_week_sum['deaths'].sum()
    df_last_week_sum['%total_EU_weekly_cases'] = df_last_week_sum.apply(lambda row: row['cases'] / total_weekly_cases,
                                                                        axis=1)
    df_last_week_sum['%total_EU_weekly_deaths'] = df_last_week_sum.apply(
        lambda row: row['deaths'] / total_weekly_deaths, axis=1)

    return df_last_week_sum


def plot_for_one_country(df, country_name):
    df_country = df[df.countriesAndTerritories == country_name]
    plot = alt.Chart(df_country, title=country_name).mark_line().encode(
            alt.X('date', scale=alt.Scale(zero=False)),
            alt.Y('cases', scale=alt.Scale(zero=False))
        ).properties(
        height=120
    )
    return plot


@st.cache(allow_output_mutation=True)
def plot_for_all_countries(df, countries, kpi, allow_output_mutation=True):
    dict_of_plots = dict()
    for country in countries:
        plot = plot_for_one_country(df, country)
        dict_of_plots[country] = plot
    return dict_of_plots


@st.cache(hash_funcs={folium.folium.Map: lambda _: None}, allow_output_mutation=True)
def create_map(country_coordinates, dict_of_plots, df_last_week_sum, kpi, df):
    europe_map = folium.Map(location=[54, 15], zoom_start=3.2, tiles='cartodbpositron')
    colormap = linear.RdYlBu_08.scale(df_last_week_sum['%total_EU_weekly_cases'].quantile(0.05),
                                      df_last_week_sum['%total_EU_weekly_cases'].quantile(0.95))
    colormap = LinearColormap(colors=list(reversed(colormap.colors)),
                              vmin=colormap.vmin,
                              vmax=colormap.vmax)
    colormap.add_to(europe_map)
    colormap.caption = "Percentage of total sum within Europe for previous week"
    colormap.add_to(europe_map)

    for country, coordinates in country_coordinates.items():
        country_plot = dict_of_plots[country]
        try:
            icon_color = colormap(df_last_week_sum.loc[country]['%total_EU_weekly_cases'])
        except:
            icon_color = 'black'
        folium.vector_layers.CircleMarker(
            tooltip=f"Country: {country}"
                    f"\nDate: {df[df.countriesAndTerritories==country].iloc[-1]['date']}"
                    f"\nNumber of cases: {df[df.countriesAndTerritories==country].iloc[-1][kpi]}",
            location=coordinates,
            fill=True,
            fill_color=icon_color,
            color=None,
            fill_opacity=0.7,
            radius=6,
            popup=folium.Popup().add_child(
                folium.features.VegaLite(country_plot)
            )
        ).add_to(europe_map)

    return europe_map


def get_pivot_df(df, date, country_column_name):
    pivot_df = df.pivot(index=date, columns=country_column_name, values=['cases', 'deaths'])
    return pivot_df


def create_dict_labels(countries, suffix):
    dict_labels = {country: f'{country}_{suffix}'  for country in countries}
    return dict_labels


def make_pivot_plots(df, countries, kpis=('cases', 'deaths'), country_column_name=constants.country_column_name,
                     date=constants.date):
    df_pivot = get_pivot_df(df, date, country_column_name)

    plot = make_subplots(specs=[[{'secondary_y': True}]])
    cases_labels = create_dict_labels(countries, kpis[0])
    deaths_labels = create_dict_labels(countries, kpis[1])
    y_axis_1 = px.line(df_pivot[kpis[0]], x=df_pivot[kpis[0]].index, y=countries)
    y_axis_2 = px.line(df_pivot[kpis[1]], x=df_pivot[kpis[1]].index, y=countries,
                       line_dash_sequence=['dot'],
                       color_discrete_sequence=px.colors.qualitative.Light24)
    y_axis_2.update_traces(yaxis='y2')
    y_axis_1.for_each_trace(lambda t: t.update(name=cases_labels[t.name],
                                               legendgroup=cases_labels[t.name],
                                               hovertemplate=t.hovertemplate.replace(t.name, cases_labels[t.name])))
    y_axis_2.for_each_trace(lambda t: t.update(name=deaths_labels[t.name],
                                               legendgroup=deaths_labels[t.name],
                                               hovertemplate=t.hovertemplate.replace(t.name, deaths_labels[t.name])))
    plot.add_traces(y_axis_1.data + y_axis_2.data)
    plot.layout.title = "Covid-19 trend plots"
    plot.layout.yaxis.title = kpis[0].upper()
    plot.layout.yaxis2.title = kpis[1].upper()
    plot.update_layout(
        autosize=False,
        width=800,
        height=500)

    return plot


