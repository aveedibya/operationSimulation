# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 12:48:10 2018
@author: Aveedibya Dey
"""
import numpy as np
import datetime as dt
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

#Internal package with functions and classes
import call_gen_demo as cgd

#-------------------------------
app = dash.Dash()
app.title = 'Operations Simulator'
server = app.server

#-------------------------------
#Define Formatting Stuff
margin={'l':50, 'b':40, 'r':40, 't':40}
yaxis = dict(zeroline = False)
xaxis = dict(zeroline = False)

def graphingRegion(height, margin=margin):
        return {'data':[], 
                'layout': go.Layout(height=height, 
                                    margin=margin, 
                                    yaxis = dict(zeroline = False, showticklabels=False, showgrid=False),
                                    xaxis = dict(zeroline = False, showticklabels=False, showgrid=False),
                                    font=dict(family='Dosis')
                                    )
                }

intro_text = '''##### About this Simulator:
This simulator was built to provide an interactive platform for running simulations on 
different staffing and scheduling scenarios. The simulator lets you input the following parameters:

- __Number of Agents:__ Enter the number of agents staffed. Current assumption is that all these agents
are staffed 24x7. This is not practical, however, it is equivalent to having a flat staff throughout the day.
A more efficient system will call for different schedules assigned to different agents to meet the changing workload demand.
This scenario will be built in future versions, but can be easily integrated in this simulator.
- __Peak Call Count:__ Lets you enter the maximum expected number of calls in an half-hour interval. Using this input, 
a call distribution is built for the entire day, assuming linear increase in the average number of calls to the peak value and then
a linear decrease in average calls. Once the average call distribution is built, actual call counts are calculated based on a random draw
from a poisson distribution assuming the average calls for that interval is based on the distribution previously generated.
- __Average Handling Time (Lower and Upper bounds):__ The average handling time or AHT includes the total time spent by agents on a call and two inputs
are taken from the user - minimum and maximum AHT expected throughout the day. Using these lower and upper bounds a random draw allows the simulator
to assign a call aht to each call in every interval. 

Once the above inputs are available, calls are generated with AHT assigned to each. These calls are then allocated to agents. Agent allocation is usually
random for agents in idle status, but if no agents are available in an interval, then the call is assigned to the agent who is available at the earliest 
to reduce the call wait time. This assignment is based on a first-in first-out assignment where the calls are sequentially queued and the first call to arrive 
will be handled first. 

__Go ahead and enter any combination of parameters you would like!__

_If you are not sure what to enter, try this: `Number of agents: 3, Peak call count: 20, AHT Lower Bound: 200, AHT Upper Bound: 250`_ 

'''
        
text_to_show = '''###### Simulation Results:

Below parameters show a summary of the statistics from the simulation that was run:

 1. __Calls: {}__
   - Total Calls: __{:.0f}__
   - Avg. Handling Time (AHT): __{:.1f} sec__
   - AHT Range in Simulation: __{:.0f}-{:.0f} sec__
   - Call Wait Time Range: __{:.1f}-{:.1f} sec__

 2. __Agent Statistics:__  
   - Total number of agents staffed: __{:.0f}__
   - All agents were assumed to be staffed 24x7

'''
#To see a distribution at an interval level, refer charts shown below. 

footnote_markdown = '''
Created by: Aveedibya Dey | [Source Code](https://github.com/aveedibya/operationSimulation) | [Contact Me/Leave Feedback](https://aveedibyadey.typeform.com/to/guGq1P) | See other creations: [Regression Simulator](https://github.com/aveedibya/regressionSimulator), [Forecasting Tool](https://ultimateforecastingtool.herokuapp.com/)
    '''

#-------------------------------
#App Layout
app.layout = html.Div(
    html.Div([
        html.H3('Operations Simulation Dashboard'),
        
        dcc.Interval(
            id='interval-component',
            interval=1*100, # in milliseconds
            n_intervals=0,
            max_intervals=600
        ), 
        html.Div(html.H6(id='animated-subtitle', children=' ', style={'line-height': '1.1', 'color': 'rgb(0, 153, 255)'})),
        
        html.Div([html.Div([html.H4('Enter Simulation Parameters:'), 
                            html.Button('Run Simulation', id='begin-simulation')], style={'width': '33%', 'display': 'inline-block'}), 
                  html.Div([html.Label('Enter Number of Agents:'), 
                            dcc.Input(id='agent-count', type='number', step=1, placeholder='#Agents'),
                            html.Label('Enter Peak Call Count:'), 
                            dcc.Input(id='max-intvl-calls', type='number', step=1, placeholder='Intvl Call Avg')], style={'width': '33%', 'display': 'inline-block'}),
                  html.Div([html.Label('Enter AHT(sec) Lower Bound:'), 
                            dcc.Input(id='aht-lower', type='number', step=50, placeholder='AHT Min'),
                            html.Label('Enter AHT(sec) Upper Bound:'), 
                            dcc.Input(id='aht-upper', type='number', step=50, placeholder='AHT Max')], style={'width': '33%', 'display': 'inline-block'})
                  ], style={'border': 'thin lightgrey solid', 'paddingLeft': '40', 'paddingBottom': '20', 'paddingTop': '10', 'backgroundColor': '', 'marginBottom': '5'}
                ),
                  
        html.Div(id='intro-text-above-graph', children=(dcc.Markdown(intro_text)), style={'backgroundColor': 'rgb(212,212,212,0.5)', 'padding': '10', 'marginTop': '1%'}),
        
        html.Div(id='graph-block', children=[
        #---
        #Call Count Graph
        html.Div([html.Div([dcc.Graph(id='live-update-graph', config={'displayModeBar': False}, figure=graphingRegion(450), clear_on_unhover=True, hoverData={'points':[{'customdata': 'showall'}]})], style={'width': '69%', 'display': 'inline-block'}),
                  html.Div(dcc.Markdown(id='simulation-details'), style={'width': '29%',  'fontSize': '80%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '5', 'paddingTop': '10'})]),
        #---
        #Call Wait Time and BP Graphs
        html.Div([dcc.Graph(id='call-wait-time-graph', config={'displayModeBar': False}, figure=graphingRegion(225)),
                  dcc.Graph(id='bp-graph', config={'displayModeBar': False}, figure=graphingRegion(225))], style={'width': '49%', 'display': 'inline-block'}),
        #---
        #Agent Status Graph
        html.Div([dcc.Graph(id='agent-view-graph', config={'displayModeBar': False}, figure=graphingRegion(450))], style={'width': '49%', 'display': 'inline-block', 'padding': '5'}),
        
        #---
        #Hidden elements storing intermediate dataframes in json 
        html.Div(id='call_table', style={'display':'none'}),
        html.Div(id='agent_table', style={'display':'none'})
        ], style={}),
                  
        html.Div(id='intro-text-below-graph', children=(dcc.Markdown(intro_text)), style={'display': 'none'}),
        
        #---------
        #Footnote
        html.Div([dcc.Markdown(footnote_markdown)], 
                  style={'borderTop': 'thin lightgrey solid', 'textAlign': 'center', 'padding': '10', 'fontSize': 'small'})
        
    ]), className= 'container'
)



#=====================================
#APP CALLBACK FUNCTIONS
#=====================================

@app.callback(Output('animated-subtitle', 'children'),
              [Input('interval-component', 'n_intervals')])
              
def update_subtitle(n):
    '''
    '''
    subtitle_text = 'EASILY RUN SIMULATIONS, GET DEEPER INSIGHTS' 
    if n%60 > 0 :
        return subtitle_text[:n%60] + '|'
    else:
        if n == 600 :
            return subtitle_text
        else:
            return '|'
    
#--------------------------------------------------
#Generate Text Section: Read Inputs and Update Text
#--------------------------------------------------
@app.callback(Output('simulation-details', 'children'),
              [Input('agent_table', 'children'),
               Input('agent-count', 'value'), 
               Input('aht-upper', 'value'), 
               Input('aht-lower', 'value'),
               Input('max-intvl-calls', 'value'),
               Input('live-update-graph', 'hoverData')]
               )
                  
def update_info_text(call_table_json, agent_count, aht_upper, aht_lower, max_intvl_calls, time_filter):
    '''
    '''
    print('-----time filter----------:', time_filter)
    call_table_df = pd.read_json(call_table_json, orient='split')
    if time_filter is not None:
        if time_filter['points'][0]['customdata'] != 'showall':
            current_hover = dt.datetime.strptime(time_filter['points'][0]['customdata'], "%Y-%m-%d %H:%M:%S")
            call_table_df = call_table_df[call_table_df['intvl_time_elapsed']==cgd.timeElapsed(current_hover)]
            show_filter_text = '(for ' + str(current_hover.time()) + ' to ' + str(cgd.timeAddition(current_hover.time(),[0,30,0])) + ')'
        else:
            show_filter_text = '(for 24 hrs)'
    else:
        show_filter_text = '(for 24 hrs)'
    #print(call_table_df)
    call_count = len(call_table_df)
    wait_min = min(call_table_df['call_wait_time_elapsed'])
    wait_max = max(call_table_df['call_wait_time_elapsed'])
    aht_lower_actual = min(call_table_df['call_aht'])
    aht_upper_actual = max(call_table_df['call_aht'])
    avg_aht = sum(call_table_df['call_aht'])/call_count
    
    return text_to_show.format(show_filter_text, call_count, avg_aht, aht_lower_actual, aht_upper_actual, wait_min, wait_max, agent_count)

#--------------------------------------------------
#Show/Hide Graphs
#--------------------------------------------------
@app.callback(Output('intro-text-above-graph', 'style'),
              [Input('agent_table', 'children')]
               )

def show_chart_block_above(agent_table):
    '''
    '''
    if agent_table is None:
        return {'backgroundColor': 'rgb(212,212,212,0.5)', 'padding': '10', 'marginTop': '1%'}
    else:
        return {'display': 'none'}

#--------------------------------------------------
#Show/Hide Graphs
#--------------------------------------------------
@app.callback(Output('intro-text-below-graph', 'style'),
              [Input('agent_table', 'children')]
               )

def show_chart_block_below(agent_table):
    '''
    '''
    if agent_table is not None:
        return {'backgroundColor': 'rgb(212,212,212,0.5)', 'padding': '10', 'marginTop': '1%'}
    else:
        return {'display': 'none'}
    

#--------------------------------------------------
#Run Simulation: Read Inputs and Generate Dataframe
#--------------------------------------------------
@app.callback(Output('agent_table', 'children'),
              [Input('begin-simulation', 'n_clicks')],
              [State('agent-count', 'value'), 
               State('aht-upper', 'value'), 
               State('aht-lower', 'value'),
               State('max-intvl-calls', 'value')]
              )

def gen_call_table(sim_click, agent_count, aht_upper, aht_lower, max_intvl_calls):
    #Create the intervals
    intvl_avg_calls = list(range(0,24,1)) + list(range(24,0,-1))
    intvl_avg_calls = [x*max_intvl_calls/max(intvl_avg_calls) for x in intvl_avg_calls]
    
    intvl_st_time_day = [(dt.datetime(2018,1,1,0,0,0) + dt.timedelta(minutes= +30*x))  for x in range(len(intvl_avg_calls))]
    intvl_st_time = [dt.time(x.hour, x.minute, x.second) for x in intvl_st_time_day]
    #Poission distribuiton random pick of call count in an interval
    intvl_call_count = [np.random.poisson(x) for x in intvl_avg_calls]
    #AHT Range
    aht_range = [int(aht_lower), int(aht_upper)]
    print('Call Table Created')
    print('------------------')
    return cgd.brandpromise(cgd.agent_table(int(agent_count), cgd.call_table(intvl_st_time, intvl_call_count, aht_range))).to_json(date_format='iso', orient='split')

#--------------------------------------------------
#Call Count Graph: Line Chart
#--------------------------------------------------
@app.callback(Output('live-update-graph', 'figure'),
              [Input('agent_table', 'children')])
def update_graph_live(call_table_json):
    '''
    '''
    #print('n is now:', n*1000)
    call_table_df_orig = pd.read_json(call_table_json, orient='split')
    call_table_df_orig['call_count'] = 1
    call_table_orig_pivot = pd.pivot_table(call_table_df_orig, values='call_count', index='intvl_start_time', aggfunc=np.sum)
    
    call_table_df = call_table_df_orig #[call_table_df_orig['intvl_time_elapsed']<n*500]
    call_table_pivot = pd.pivot_table(call_table_df, values='call_count', index='intvl_start_time', aggfunc=np.sum)
    #print(call_table_df)
    traces=[]
    
    traces.append(go.Scatter(
            x=call_table_pivot.index,
            y=call_table_pivot['call_count'],
            customdata=cgd.timeElapsed(call_table_pivot.index),
            mode='lines+markers', 
            opacity = 0.8,
            line = dict(color = ('rgb(22, 96, 167)'),
                        width = 4),     
            name='Call Count',
            marker = dict(size = 10)
            ))
    
    return {
        'data': traces,
        'layout': go.Layout(
            height=450,
            margin=margin,
            title="Call Count by Intervals",
            xaxis={'title': '', 'range':[min(call_table_df_orig['intvl_start_time']), max(call_table_df_orig['intvl_start_time'])], 'zeroline': False},
            yaxis={'title': '', 'range':[0, max(call_table_orig_pivot['call_count'])*1.1], 'zeroline': False},
            hovermode='closest',
            font=dict(family='Raleway')
        )
    }


#--------------------------------------------------
#Call Wait Time Graph: Scatter Plot
#--------------------------------------------------
@app.callback(Output('call-wait-time-graph', 'figure'),
              [Input('agent_table', 'children'),
               Input('live-update-graph', 'hoverData')])
def update_wait_time_graph(agent_table_json, time_filter):
    '''
    '''
    agent_table_df = pd.read_json(agent_table_json, orient='split')
    #print('agent_table: ', agent_table_df_orig)
    
    current_hover = None
    if time_filter is not None:
        if time_filter['points'][0]['customdata'] != 'showall':
            current_hover = dt.datetime.strptime(time_filter['points'][0]['customdata'], "%Y-%m-%d %H:%M:%S")
    
    if current_hover is not None:
            agent_table_df = agent_table_df[agent_table_df['intvl_time_elapsed'] == cgd.timeElapsed(current_hover)].reset_index()

    traces=[]
    colorlist = []
    
    for x in agent_table_df['call_wait_time_elapsed'].tolist():
        if x > 60:
            colorlist.append('rgb(244,109,67)') #Red
        else:
            colorlist.append('rgb(128,205,193)') #Green
            
    traces.append(go.Scatter(
            x=agent_table_df['call_handle_start_time'],
            y=agent_table_df['call_wait_time_elapsed'],
            mode='markers', 
            marker={'color': colorlist, 'opacity': 0.8, 'line': {'width': 0.5, 'color': 'white'}},
            name=''))
    
    return {
        'data': traces,
        'layout': go.Layout(
            height=225,
            margin=margin,
            title="Avg. Call Wait Time: {:.2f} sec".format(round(sum(agent_table_df['call_wait_time_elapsed'])/float(len(agent_table_df))),2),
            xaxis={'zeroline': False},
            yaxis={'title': '', 'range':[0, max(agent_table_df['call_wait_time_elapsed'])*1.1], 'zeroline': False},
            hovermode='closest',
            font=dict(family='Raleway')
        )
    }
    
#--------------------------------------------------
#Agent Status Graph: Horizontal Stacked Bar Chart
#--------------------------------------------------
@app.callback(Output('agent-view-graph', 'figure'),
              [Input('agent_table', 'children'),
               Input('live-update-graph', 'hoverData')])
def update_agent_view(agent_table_json, time_filter):
    '''
    '''
    agent_table_df_orig = pd.read_json(agent_table_json, orient='split')
    #print('agent_table: ', agent_table_df_orig)
    current_hover = None
    if time_filter is not None:
        if time_filter['points'][0]['customdata'] != 'showall':
            current_hover = dt.datetime.strptime(time_filter['points'][0]['customdata'], "%Y-%m-%d %H:%M:%S")
 
    agent_table_df = agent_table_df_orig 
    
    traces=[]
    hovertext=[]
    occupancy=[]
    total_busy_time=[]
    total_agent_time=[]
    
    for agent in agent_table_df['agent_index'].drop_duplicates().sort_values().tolist():
        curr_agent = cgd.agentStatusMatrix(agent_table_df[agent_table_df['agent_index']==agent][['call_handle_start_time', 'call_handle_time_elapsed', 'call_end_time', 'call_end_time_elapsed', 'call_aht']])
        if current_hover is not None:
            curr_agent = curr_agent[(curr_agent['call_handle_time_elapsed'] > cgd.timeElapsed(current_hover)) & (curr_agent['call_handle_time_elapsed'] < cgd.timeElapsed(cgd.timeAddition(current_hover, [0,30,0])))].reset_index()
        curr_agent['agent_index'] = 'Agent-' + str(agent)
        #print('-----------------')
        #print(curr_agent)
        #Create a colorlist for busy/available status
        colorlist = []
        #Create a list for agent status
        agent_status = []
        iterator=0
        
        for x in curr_agent['status'].tolist():
            
            if x == 1:
                colorlist.append('rgb(244,109,67)') #Red
                agent_status.append('Agent is Busy at: ' + str(curr_agent['call_handle_start_time'][iterator]))
            else:
                colorlist.append('rgb(166,217,106)') #Green
                agent_status.append('Agent is Idle at: ' + str(curr_agent['call_handle_start_time'][iterator]))
            iterator +=1
        
            total_busy_time.append(sum(curr_agent[curr_agent['status']==1]['time_gaps']))
            total_agent_time.append(sum(curr_agent['time_gaps']))
            occupancy.append(total_busy_time[agent]/total_agent_time[agent])
        
        traces.append(go.Bar(
                x=curr_agent['time_gaps'],
                y=curr_agent['agent_index'],
                text=agent_status,
                hoverinfo='text',
                orientation = 'h',
                marker = dict(color=colorlist, opacity=0.5),
                name=''))
    
    return {
        'data': traces,
        'layout': go.Layout(
            height=450,
            margin=margin,
            title="Overall Occupancy: {0:.1%}".format(float(sum(total_busy_time))/float(sum(total_agent_time))),
            xaxis={'title': '', 'zeroline': False, 'showgrid': False, 'showticklabels': False},
            yaxis={'zeroline': False, 'showgrid': False},
            hovermode='closest',
            barmode='stack',
            showlegend=False,
            font=dict(family='Raleway')
        )
    }
    
#--------------------------------------------------
#Brand Promise Graph: Vertical Bar Chart
#--------------------------------------------------
@app.callback(Output('bp-graph', 'figure'),
              [Input('agent_table', 'children'),
               Input('live-update-graph', 'hoverData')])
def update_bp(agent_table_json, time_filter):
    '''
    '''
    agent_table_df = pd.read_json(agent_table_json, orient='split')
    
    current_hover = None
    if time_filter is not None:
        if time_filter['points'][0]['customdata'] != 'showall':
            current_hover = dt.datetime.strptime(time_filter['points'][0]['customdata'], "%Y-%m-%d %H:%M:%S")
    
    if current_hover is not None:
            agent_table_df = agent_table_df[agent_table_df['intvl_time_elapsed'] == cgd.timeElapsed(current_hover)].reset_index()

    agent_table_df['call_count'] = 1
    bp_table = pd.pivot_table(agent_table_df, values=['call_count', 'bp_ind'], index='intvl_start_time', aggfunc=np.sum)
    bp_table['bp'] = bp_table['bp_ind']/bp_table['call_count']
    
    traces=[]
    colorlist = []
    
    for bp in bp_table['bp'].tolist():
        if bp < 0.90:
            colorlist.append('rgb(244,109,67)') #Red
        else:
            colorlist.append('rgb(128,205,193)') #Green

    traces.append(go.Bar(
                x=bp_table.index,
                y=bp_table['bp'],
                marker = dict(color=colorlist),
                name='Interval-level Brand Promise'))
    
    return {
        'data': traces,
        'layout': go.Layout(
            height=225,
            margin=margin,
            title="Brand Promise: {0:.1%}".format(sum(bp_table['bp'])/float(len(bp_table))),
            xaxis={'title': '', 'zeroline': False},
            yaxis={'title': '', 'range':[0, 1], 'zeroline': False, 'tickformat': ',.0%', 'hoverformat': ",.1%"},
            hovermode='closest',
            font=dict(family='Raleway')
        )
    }


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/0e463810ed36927caf20372b6411690692f94819/dash-drug-discovery-demo-stylesheet.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

#app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == '__main__':
    app.run_server(debug=True)
