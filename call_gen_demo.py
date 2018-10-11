# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 11:36:04 2018
@author: Aveedibya Dey
"""
import numpy as np
import random
import pandas as pd
import datetime as dt

#Define some attributes of a call
class inboundCall:
    """
    """
    call_type = 'inbound'
    
    def __init__(self, aht_range, arrival_intvl):
        self.aht_actual = random.randint(aht_range[0], aht_range[1])
        self.call_start_time = dt.time(arrival_intvl.hour, arrival_intvl.minute + random.randint(1,29))

#Generate call table with call attributes
def call_table(intvl_st_time, intvl_call_count, aht_range):
    '''
    '''
    col_name = ['intvl_start_time','call_start_time', 'call_aht', 'call_end_time', 'call_st_time_elapsed', 'intvl_time_elapsed']
    call_table_df = pd.DataFrame(columns=col_name)
    
    for i in range(len(intvl_st_time)):
        #print()
        #print(i)
        for j in range(intvl_call_count[i]):
            #print(j)
            currCallStart = inboundCall(aht_range, intvl_st_time[i]).call_start_time
            currCallAHT = inboundCall(aht_range, intvl_st_time[i]).aht_actual
            int_df = pd.DataFrame({col_name[0]: intvl_st_time[i],
                                   col_name[1]: currCallStart,
                                   col_name[2]: currCallAHT,
                                   col_name[3]: timeAddition(currCallStart, [0,0,currCallAHT]),
                                   col_name[4]: currCallStart.hour*3600 + currCallStart.minute*60 + currCallStart.second,
                                   col_name[5]: intvl_st_time[i].hour*3600 + intvl_st_time[i].minute*60 + intvl_st_time[i].second}, index=[0])
            #print(int_df)
            call_table_df = call_table_df.append(int_df, ignore_index=True)
        
    return call_table_df.sort_values(by=col_name[1]).reset_index().drop('index', 1)



#Agent attributes
#agent_start_time = dt.time(8,0)
#agent_end_time = dt.time(18,0)

#Assumption 1: Agents are staffed 24x7:

def agent_table(agent_count, call_table_df):
    '''
    Input 1: 'agent_count': number of agents staffed
    Input 2: 'call_table_df': detailed call table with call start times and AHTs
    '''
    agent_status = [1 for x in range(agent_count)]
    col_name = ['call_index','agent_index', 'call_handle_start_time', 'call_aht','call_end_time', 'call_wait_time', 'call_handle_time_elapsed',
                'intvl_start_time','call_arrival_time', 'intvl_time_elapsed', 'call_end_time_elapsed', 'call_wait_time_elapsed']
    agent_table_df = pd.DataFrame(columns=col_name)
    
    
    for i in range(len(call_table_df)):
        
        agent_status = updateAgentStatus(call_table_df['call_start_time'][i], agent_status, agent_table_df)
        agentPicked = assignCalltoAgent(agent_status, agent_table_df)
        #print('agent picked is: ',agentPicked)
        #print('Agent Status List: ', agent_status)
        
        if agent_status[agentPicked] == 1:
            call_handle_start_time = call_table_df['call_start_time'][i]
            call_wait_time = 0
        else:
            call_handle_start_time = agentNextAvail(agent_status, agent_table_df)[agentPicked]
            call_wait_time = timeAddition(call_handle_start_time, [-call_table_df['call_start_time'][i].hour, -call_table_df['call_start_time'][i].minute, -call_table_df['call_start_time'][i].second])
        
        int_df = pd.DataFrame({col_name[0]: i,
                               col_name[1]: agentPicked,
                               col_name[2]: call_handle_start_time,
                               col_name[3]: call_table_df['call_aht'][i],
                               col_name[4]: timeAddition(call_handle_start_time, [0,0,call_table_df['call_aht'][i]]),
                               col_name[5]: call_wait_time,
                               col_name[6]: timeElapsed(call_handle_start_time),
                               col_name[7]: call_table_df['intvl_start_time'][i],
                               col_name[8]: call_table_df['call_start_time'][i],
                               col_name[9]: call_table_df['intvl_time_elapsed'][i],
                               col_name[10]: timeElapsed(timeAddition(call_handle_start_time, [0,0,call_table_df['call_aht'][i]])),
                               col_name[11]: timeElapsed(call_wait_time)
                              }, index=[0])
        #print(int_df)
        agent_table_df = agent_table_df.append(int_df, ignore_index=True)
        
    
    return agent_table_df

def updateAgentStatus(update_for_time, agent_status, agent_table_df):
    '''
    '''
    #Reset agent_status list
    agent_status = [1 for x in range(len(agent_status))]
    #Find list of agents accupied
    agents_occupied = agent_table_df[agent_table_df['call_end_time']>update_for_time]['agent_index'].drop_duplicates().tolist()
    
    for i in range(len(agents_occupied)):
        agent_status[agents_occupied[i]] = -1
        
    return agent_status

#Find the next available agent
def agentNextAvail(agent_status, agent_table_df):
    '''
    '''
    agentAvail = agent_status.copy()
    for i in range(len(agent_status)):
        if agent_status[i] == -1:
            #print(agent_table_df)
            agentAvail[i] = max(agent_table_df[agent_table_df['agent_index']==i]['call_end_time'])
        else:
            agentAvail[i] = dt.time(0,0,0)
    #print('Agent Available List: ', agentAvail)
    return agentAvail

#Define a function to pick an agent randomly out of available agent at a point in time
def assignCalltoAgent(agent_status, agent_table_df):
    '''
    '''
    if 1 not in agent_status:
        agent_avail_list = agentNextAvail(agent_status, agent_table_df)
        return agent_avail_list.index(min(agent_avail_list))
    else:
        pick_randomAgent = random.randint(0,len(agent_status)-1)
        while agent_status[pick_randomAgent]!=1:
            pick_randomAgent = random.randint(0,len(agent_status)-1)
        return pick_randomAgent
        
#Function to add time with time
def timeAddition(baseTime, AddHourMinuteSecCSV=[0,0,0]):
    '''
    '''
    temp_date = dt.datetime(2018, 1, 1, baseTime.hour, baseTime.minute, baseTime.second) + dt.timedelta(hours=AddHourMinuteSecCSV[0], minutes=AddHourMinuteSecCSV[1], seconds=AddHourMinuteSecCSV[2])
    return dt.time(temp_date.hour, temp_date.minute, temp_date.second)

#Function to create a time stamp list to show live updates
def liveTime(df):
    '''
    '''
    nowtime = dt.datetime.now()

    for i in range(len(df)):
        #print(i)
        df[df.columns[0]][i] = timeAddition(df[df.columns[0]][i], [nowtime.hour, nowtime.minute, nowtime.second])
    
    return df

def timeElapsed(dt_time):
    '''
    '''
    if type(dt_time) == dt.time:
        return dt_time.hour*3600 + dt_time.minute*60 + dt_time.second
    elif type(dt_time) == dt.datetime:
        print('Warning: datetime object was passed to timeElapsed function\n timeElapsed will only calculate based on the time and IGNORE date part')
        return dt_time.hour*3600 + dt_time.minute*60 + dt_time.second
    else:
        print('Warning: datetime object not provided, type:', type(dt_time))
        return dt_time

def agentStatusMatrix(agent_df):
    '''
    Required columns: 'call_handle_time_elapsed', 'call_end_time_elapsed', 'call_aht'
    '''
    agent_df_singular = agent_df[['call_handle_start_time', 'call_handle_time_elapsed']].append(agent_df[['call_end_time', 'call_end_time_elapsed']].rename(columns={'call_end_time': 'call_handle_start_time', 'call_end_time_elapsed': 'call_handle_time_elapsed'})).sort_values(by='call_handle_time_elapsed').reset_index().drop('index',1)
    agent_df_timegap = agent_df_singular['call_handle_time_elapsed'][1:].reset_index().drop('index',1) - agent_df_singular['call_handle_time_elapsed'][:len(agent_df_singular)-1].reset_index().drop('index',1)
    #print(agent_df_timegap)
    agent_df_singular['time_gaps'] = 0
    agent_df_singular['time_gaps'][1:] = agent_df_timegap['call_handle_time_elapsed'][:]
    agent_df_singular['time_gaps'][0] = agent_df_singular['call_handle_time_elapsed'][0]
    agent_df_singular['status'] = 1 #Default all to busy status
    agent_df_singular['status'][agent_df_singular.index%2==0] = 0 #Even indices are changed to available
    
    return agent_df_singular

def brandpromise(agent_df, bp=60, wait_time_col='call_wait_time_elapsed'):
    '''
    '''
    agent_df['bp_ind'] = 1 #1 indicates call wait time meets brand promise requirement
    agent_df['bp_ind'][agent_df[wait_time_col]>bp] = 0
    print('-----------------------')
    print('Added Brand Bromise columns based on ', bp, ' sec wait time')
    return agent_df
        
if __name__ =='__main__':
    pass