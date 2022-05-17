# Import required libraries
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import Dash, html, dcc, Input, Output
from dash import no_update

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

def assign_marker_color(booster_cat):
    if booster_cat == "v1.0":
        return 'green'
    elif booster_cat == "v1.1":
        return 'blue'
    elif booster_cat == "FT":
        return 'yellow'
    elif booster_cat == "B4":
        return 'red'
    elif booster_cat == "B5":
        return 'purple'

spacex_df['Booster_cat_color'] = spacex_df['Booster Version Category'].apply(assign_marker_color)
print(spacex_df.head())

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', 
                                                options=[
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                    ],
                                                value= 'ALL',
                                                placeholder= 'Select a Launch Site',
                                                searchable= True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=100, marks={0: '0', 100: '100', 10000: '10000'}, value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(["output", dcc.Graph(id='success-payload-scatter-chart')]),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'),
               )
def get_pie_chart(entered_site):
    filtered_df = spacex_df.groupby(['LaunchSite'])['class'].mean().reset_index()
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class',
        names='LaunchSite', 
        title='Piechart for Launch Sites')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = filtered_df[filtered_df['LaunchSite']==entered_site]
        other_df = pd.DataFrame(['other', (1 - float(filtered_df['class']))], index=['LaunchSite', 'class']).transpose()
        new_df = pd.concat([filtered_df, other_df], ignore_index=True)
        fig = px.pie(new_df, values='class', 
        names=['Succes', 'Failure'],
        title='Piechart for {}'.format(entered_site))
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
                [Input(component_id='site-dropdown', component_property='value'),
                Input(component_id='payload-slider', component_property='value')]
               )
def get_scatter_chart(entered_site, selected_payload):
    filtered_df = spacex_df[['LaunchSite',"Payload Mass (kg)", 'class', 'Booster Version Category']]       
    filtered_PL_LS_df = filtered_df[filtered_df["Payload Mass (kg)"] <= selected_payload[1]]
    filtered_PL_LS_df = filtered_PL_LS_df[filtered_PL_LS_df["Payload Mass (kg)"] >= selected_payload[0]]
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_PL_LS_df,
            x='Payload Mass (kg)', 
            y='class', 
            color=filtered_PL_LS_df['Booster Version Category'])
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_LS_df = filtered_PL_LS_df[filtered_df['LaunchSite'] == entered_site]
        fig = px.scatter(
            filtered_LS_df,
            x="Payload Mass (kg)",
            y='class', 
            color=filtered_LS_df['Booster Version Category'])
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
