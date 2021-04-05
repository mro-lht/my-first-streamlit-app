import streamlit as st
import streamlit_wordcloud as wordcloud
import json
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from tinydb import TinyDB, Query
import pandas as pd
import matplotlib
import plotly.express as px




#Calculate HEX value from RGB value
@st.cache
def get_HEX_value(min_value, max_value, actual_value):

    #read Viridis RGB values from Excel
    rgb_data = pd.read_excel('Viridis_RGB.xlsx')

    #Fill dataframe
    rgb_df = pd.DataFrame(rgb_data, columns = ['R','G','B'])

    #0..255
    if min_value == 0:
        min_value = 1

    if actual_value == 0:
        actual_value = 1

    #norm value to scale and round
    norm_val = int(round(((actual_value-min_value)/(max_value-min_value))*255))

    #calculate HEX value
    return matplotlib.colors.to_hex([rgb_df.R[norm_val], rgb_df.G[norm_val], rgb_df.B[norm_val]])


streamlit_color = '#d3093e'

#Initialize database
db = TinyDB('db.json')

st.title('Data usage questionaire')

st.write('Welcome to our short data source usage questionaire.')

st.header('0. Organization')

#db.drop_table('org')
#db.drop_table('role')
#db.drop_table('apps')
#db.drop_table('connections')
#db.drop_table('challenges')

#Save org unit
org_table = db.table('org')

#Add business segments to database if not existing
if len(org_table) == 0:
    org_table.insert_multiple([
        {"text": "Aircraft Maintenance", "value": 0, "short": "Aircraft"},
        {"text": "Central Services", "value": 0, "short": "Central"},
        {"text": "Component Services", "value": 0, "short": "Component"},
        {"text": "Digital Fleet Solutions", "value": 0, "short": "Digital"},
        {"text": "Engine Services", "value": 0, "short": "Engine"},
        {"text": "OEM, Special Mission & Modifications", "value": 0, "short": "OEM"}])

existing_org = []

#read existing app names
for org in org_table:
    existing_org.append(org['text'])

#display existing business segments in dropdown menu
user_bs_select = st.selectbox(
     'Which Business Segment do you belong to?',
     existing_org)

left_column, right_column = st.beta_columns(2)
add_org_button = left_column.button('Save', key=0)

#save org
if add_org_button:

    for org in org_table:
        #update org value
        if (org['text'] == user_bs_select):

            OrgQuery = Query()
            org_table.update({'value': org['value'] + 1}, OrgQuery.text == user_bs_select)

existing_org = []
existing_org_value = []

#read existing app names
for org in org_table:
    existing_org.append(org['text'])
    existing_org_value.append(org['value'])

#make dataframe out of DB entries
org_df = pd.json_normalize(org_table.all())

org_fig = px.bar(
    org_df,
    y='value',
    x='text',
    labels={'value':'', 'text':''},
    color="value",
    color_continuous_scale=px.colors.sequential.Viridis,
    template="simple_white"
)
# Plot!
st.plotly_chart(org_fig, use_container_width=True)



st.header('1. Role and Skill')

#Initialize role databse
role_table = db.table('role')

#add business segments to database if not existing
if len(role_table) == 0:
    role_table.insert_multiple([
        {"role": "Data Scientist", "value": 0},
        {"role": "Data Engineer", "value": 0},
        {"role": "Process Center", "value": 0},
        {"role": "Data Analyst", "value": 0}])

existing_role = []

#Read existing app names
for role in role_table:
    existing_role.append(role['role'])

user_role_select = st.selectbox(
     'How would you describe your current role when it comes to data?',
     existing_role)

skill_level = st.slider('How would you rate your skill level on a scale from 1 (beginner) to 5 (expert)?', 1, 5, 3)

left_column, right_column = st.beta_columns(2)
#add_role_button = left_column.button('Save', key=3)



st.header('2. Data Sources')

#Initialize apps database
apps_table = db.table('apps')

#Add some apps initially
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

#Sort app names
existing_apps.sort(key=lambda v: v.upper())

#Display existing apps in dropdown menu
user_app_select = st.multiselect(
     'Choose your most used data source',
     existing_apps)

user_app_input = ''

if st.checkbox('Not found your data source? No worries, just add it.'):

    #add non-existing app via text input
    user_app_input = st.text_input('Add a new data source')

#Save dialog
left_column, right_column = st.beta_columns(2)
add_ds_button = left_column.button('Save', key=1)

#Check if app name exists
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
    'text':'Data source', 'value':'Votes'})

existing_apps_value = []
existing_apps = []

#read existing app names
for app in apps_table:
    existing_apps_value.append(app['value'])
    existing_apps.append(app['text'])

with st.beta_expander('See votes per data source'):

    #Make dataframe out of DB entries
    app_df = pd.json_normalize(apps_table.all())

    #Configure bar chart
    app_fig = px.bar(
        app_df,
        x='value',
        y='text',
        labels={'value':'', 'text':''},
        color="value",
        color_continuous_scale=px.colors.sequential.Viridis,
        template="simple_white"
    )
    # Plot!
    st.plotly_chart(app_fig, use_container_width=True)



st.header('3. Data Dependencies')

connections_table = db.table('connections')
existing_connections = []

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

#Prepare network
g = Network('500px', '680px')

#Add nodes with votes
min_rel_sum = 1000000
max_rel_sum = 0
app_sum_array = {}
min_conn = 1000000
max_conn = 0


for app in apps_table:

    #Get all relations and sum up connections via dataframe
    AppRelQuery = Query()
    rel_df = pd.json_normalize(
        connections_table.search(
            (AppRelQuery.from_app == app['text']) | (AppRelQuery.to_app == app['text'])
        )
    )

    if len(rel_df) > 0:

        rel_sum = int(rel_df['value'].sum())
        rel_min = int(rel_df['value'].min())
        rel_max = int(rel_df['value'].max())

        if rel_sum > max_rel_sum:
            max_rel_sum = rel_sum
        if rel_sum < min_rel_sum:
            min_rel_sum = rel_sum

        if rel_min < min_conn:
            min_conn = rel_min
        if rel_max > max_conn:
            max_conn = rel_max

        app_sum_array[app['text']] = rel_sum

    else:
        app_sum_array[app['text']] = 0
        min_conn = 0

for app in apps_table:

    #Calculate color out of node size
    hex_rel_value = get_HEX_value(min_rel_sum, max_rel_sum, app_sum_array[app['text']])

    #Add node
    g.add_node(app['text'], size=app_sum_array[app['text']], title= app['text'] + ': ' + str(app_sum_array[app['text']]), color=hex_rel_value, border='3px')

#Add edges
for conn in connections_table:

    #Calculate color out of node size
    hex_conn_value = get_HEX_value(min_conn, max_conn, conn['value'])

    #Add edge
    g.add_edge(conn['from_app'], conn['to_app'], value=conn['value'], title= conn['value'], color=hex_conn_value)

#Display graph
HtmlFile = open("basic.html", 'r', encoding='utf-8')
source_code = HtmlFile.read()
components.html(source_code, height =600,width=1000)

g.show("basic.html")



st.header('4. Challenges')

#Read apps from db
chall_table = db.table('challenges')

#Add some apps initially
if len(chall_table) == 0:
    chall_table.insert_multiple([
        {"text": "Accessability", "value": 0},
        {"text": "Findability", "value": 0},
        {"text": "Meaning", "value": 0},
        {"text": "Tooling", "value": 0},
        {"text": "Quality", "value": 0},
        {"text": "Responsibility", "value": 0}])

existing_chall = []

#read existing app names
for chall in chall_table:
    existing_chall.append(chall['text'])

#sort app names
existing_chall.sort(key=lambda v: v.upper())

#display existing apps in dropdown menu
user_chall_select = st.multiselect(
     'Choose your most critical data challenges',
     existing_chall)

user_chall_input = ''

if st.checkbox('Not found your data challenge? No worries, just add it.'):

    #add non-existing app via text input
    user_chall_input = st.text_input('Add a new data challenge')

#save dialog
left_column, right_column = st.beta_columns(2)
add_ch_button = left_column.button('Save', key=4)

#Check if app name exists
if add_ch_button:
    found_chall = False

    #upsert???

    for chall in chall_table:
        #Update app value
        if (chall['text'] == user_chall_input) or (chall['text'] in user_chall_select):
            found_chall = True
            chall['value'] = chall['value'] + 1

            ChallQuery = Query()
            chall_table.update({'value': chall['value']}, ChallQuery.text == chall['text'])

    #Add app name
    if found_chall == False:
        #Add unknown challenge
        chall_table.insert(dict(text=user_chall_input, value=1))

existing_chall_value = []
existing_chall = []

#Read existing app names
for chall in chall_table:
    existing_chall_value.append(chall['value'])
    existing_chall.append(chall['text'])

#Make dataframe out of DB entries
chall_df = pd.json_normalize(chall_table.all())

#Configure bar chart
chall_fig = px.bar(
    chall_df,
    x='value',
    y='text',
    labels={'value':'', 'text':''},
    color="value",
    color_continuous_scale=px.colors.sequential.Viridis,
    #color_discrete_sequence = ['#d3093e'],
    template="simple_white"
)

# Plot!
st.plotly_chart(chall_fig, use_container_width=True)
