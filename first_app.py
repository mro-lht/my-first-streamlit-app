import streamlit as st
import streamlit_wordcloud as wordcloud
import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd
import streamlit.components.v1 as components
import random
from random import *


st.title('Data usage questionaire')

st.subheader('0. Your Business Segment')

#display existing apps in dropdown menu
user_bs_select = st.selectbox(
     'Which Business Segment do you belong to?',
     ['Components', 'Digital', 'Maintenance'])


st.subheader('1. Most relevant data sources')

#read from json_file
with open('apps.json') as json_file:
    apps = json.load(json_file)

existing_apps = []

#read existing app names
for app in apps:
    existing_apps.append(app['text'])

#sort app names
existing_apps.sort(key=lambda v: v.upper())

#display existing apps in dropdown menu
user_app_select = st.multiselect(
     'Choose your most used data source',
     existing_apps)

user_app_input = ''

if st.checkbox('Not found your data source? Just add it.'):

    #add non-existing app via text input
    user_app_input = st.text_input('Add a new data source')

    #ack dialoge
    left_column, right_column = st.beta_columns(2)
    added_button = left_column.button('Add')
    if added_button:
        right_column.write('Added data source ' + user_app_input)

#ack dialoge
left_column, right_column = st.beta_columns(2)
add_ds_button = left_column.button('Save', key=1)

#check if app name exists
if add_ds_button:
    found_app = False
    for app in apps:
        #update app value
        if (app['text'] == user_app_input) or (app['text'] in user_app_select):
            found_app = True
            app['value'] = app['value'] + 1

    #add app name
    if found_app == False:
        apps.append(dict(text=user_app_input, value=1))

    #write to json_file
    with open('apps.json', 'w') as json_file:
        json.dump(apps, json_file)
    right_column.write('Updated Wordcloud')

#show wordcloud
word_cld = wordcloud.visualize(apps, tooltip_data_fields={
    'text':'Data source', 'value':'Count'})

#different charts
#with st.beta_expander('See votes'):
#    chart_data = pd.DataFrame(
#         apps,
#         columns=["text", "value"])
#
#    st.bar_chart(chart_data)

st.subheader('2. Most relevant data source connections')

existing_connections = []

#read connections
with open('connections.json') as json_file:
    existing_connections = json.load(json_file)

left_column, right_column = st.beta_columns(2)

#selct from data source
user_app_from_conn_select = left_column.selectbox(
     'I often combine data from...',
     existing_apps, key=2)

#select to data source
user_app_to_conn_select = right_column.selectbox(
     'and...',
     existing_apps, key=3)

#add connection
add_conn_button = left_column.button('Save', key=2)

if add_conn_button:

    found_conn = False
    for conn in existing_connections:
        #update app value
        if (((conn['from_app'] == user_app_from_conn_select) and (conn['to_app'] == user_app_to_conn_select))
            or ((conn['from_app'] == user_app_to_conn_select) and (conn['to_app'] == user_app_from_conn_select))):
            found_conn = True
            conn['value'] = conn['value'] + 1

    #add conn name
    if found_conn == False:
        existing_connections.append(dict(from_app=user_app_from_conn_select, to_app=user_app_to_conn_select, value=1))

    #write to json_file
    with open('connections.json', 'w') as json_file:
        json.dump(existing_connections, json_file)
    right_column.write('Updated graph')

#prepare network
g = Network()

#add nodes with votes
for app in apps:
    g.add_node(app['text'], size=app['value']*10, borderWidth=3, title= app['text'] + ': ' + str(app['value']))

#add random edges
for conn in existing_connections:
    g.add_edge(conn['from_app'], conn['to_app'], value=conn['value'], title= conn['value'], color='#FFAD00')

g.show("basic.html")

#display graph
HtmlFile = open("basic.html", 'r', encoding='utf-8')
source_code = HtmlFile.read()
components.html(source_code, height =600,width=1000)
