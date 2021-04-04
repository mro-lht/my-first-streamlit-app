import streamlit as st
import streamlit_wordcloud as wordcloud
import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import streamlit.components.v1 as components
from tinydb import TinyDB, Query

st.title('Data usage questionaire')

st.subheader('0. Your Business Segment')

#display existing apps in dropdown menu
user_bs_select = st.selectbox(
     'Which Business Segment do you belong to?',
     ['Components', 'Digital', 'Maintenance'])


st.subheader('1. Most relevant data sources')

#read from json_file
db = TinyDB('db.json')
apps_table = db.table('apps')

if len(apps_table) == 0:
    apps_table.insert_multiple([
        {"text": "t/track", "value": 1},
        {"text": "m/techlog", "value": 1},
        {"text": "m/archive", "value": 1},
        {"text": "m/archive", "value": 1},
        {"text": "m/material", "value": 1},
        {"text": "L/Stage", "value": 1},
        {"text": "MAX", "value": 1},
        {"text": "linX", "value": 1},
        {"text": "Telos", "value": 1},
        {"text": "SAP BW", "value": 1}])

existing_apps = []

#read existing app names
for app in apps_table:
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

#save dialog
left_column, right_column = st.beta_columns(2)
add_ds_button = left_column.button('Save', key=1)

#check if app name exists
if add_ds_button:
    found_app = False

    #upsert???

    for app in apps_table:
        #update app value
        if (app['text'] == user_app_input) or (app['text'] in user_app_select):
            found_app = True
            app['value'] = app['value'] + 1

            AppQuery = Query()
            apps_table.update({'value': app['value']}, AppQuery.text == app['text'])

    #add app name
    if found_app == False:
        #add unknown app
        apps_table.insert(dict(text=user_app_input, value=1))

        #user feedback that entry was saved
        right_column.write('Updated Wordcloud')


#show wordcloud
word_cld = wordcloud.visualize(apps_table.all(), tooltip_data_fields={
    'text':'Data source', 'value':'Count'})

#different charts
#with st.beta_expander('See votes'):
#    chart_data = pd.DataFrame(
#         apps,
#         columns=["text", "value"])
#
#    st.bar_chart(chart_data)

st.subheader('2. Most relevant data source connections')

connections_table = db.table('connections')
existing_connections = []

if len(connections_table) == 0:
    connections_table.insert_multiple([
        {"from_app": "SAP BW", "to_app": "t/track", "value": 1},
        {"from_app": "MAX", "to_app": "t/track", "value": 1}])

#read connections
for connection in connections_table:
    existing_connections.append(connection)

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

            ConnQuery = Query()
            connections_table.update({'value': conn['value']}, (ConnQuery.from_app == conn['from_app']) & (ConnQuery.to_app == conn['to_app']))

            #acknowledge update
            right_column.write('Updated existing connection')

    #add conn name
    if found_conn == False:
        connections_table.insert(dict(from_app=user_app_from_conn_select, to_app=user_app_to_conn_select, value=1))

        #acknowledge insert
        right_column.write('Added new connection')

#prepare network
g = Network()

#add nodes with votes
for app in apps_table:
    g.add_node(app['text'], size=app['value']*10, borderWidth=3, title= app['text'] + ': ' + str(app['value']))

#add edges
for conn in connections_table:
    g.add_edge(conn['from_app'], conn['to_app'], value=conn['value'], title= conn['value'])#, color='#FFAD00')

g.show("basic.html")

#display graph
HtmlFile = open("basic.html", 'r', encoding='utf-8')
source_code = HtmlFile.read()
components.html(source_code, height =600,width=1000)
