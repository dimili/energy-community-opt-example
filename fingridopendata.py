# https://data.fingrid.fi/open-data-api/

# Data ID
#  74 Electricity production in Finland (MWh/h)
# 124 Electricity consumption in Finland (MWh/h)
# 192 Electricity production in Finland - real time data (MW)
# 193 Electricity consumption in Finland - real time data (MW)
# 265 Emission factor for electricity consumed in Finland (gCO2/kWh)
# 266 Emission factor of electricity production in Finland (gCO2/kWh)


# Response Messages
# 404 	Invalid variable id
# 416 	Requested row count is too large
# 503 	The variable is currently on maintenance break


import requests
import pandas as pd 
from dateutil.relativedelta import relativedelta


def get_open_data(api_key, variable_id, start_time, end_time, api_version = 'v1'):
    
    
    ## Example
    # from fingridopendata import get_open_data
    #
    # api_key = 'your_api_key'
    # variable_id = 265
    # start_time = 'yyyy-MM-dd HH:mm'
    # end_time = 'yyyy-MM-dd HH:mm'  
    #
    # df = get_open_data(api_key, variableid, start_time, end_time)    

    
    # Convert datetime string
    t1 = pd.to_datetime(start_time)
    t2 = pd.to_datetime(end_time)

    s1 = t1.strftime("%Y-%m-%dT%H:%M:%SZ")
    s2 = t2.strftime("%Y-%m-%dT%H:%M:%SZ")

    
    url = 'https://api.fingrid.fi/{}/variable/{}/events/json'.format(api_version, variable_id)
    
    headers = {"x-api-key": api_key}
    parameters = {'start_time': s1, \
                  'end_time': s2} 
    
    print('Calling API ...')        
    r = requests.get(url, params=parameters, headers=headers)

    # r.url


    if r.status_code == 200:
        
        d = r.json()
        # Convert to dataframe
        if len(d)==0:
            print('No data for this period')
            return
        else:
            df = pd.DataFrame(d)
            df['start_time'] =  pd.to_datetime(df['start_time'])
            df['end_time'] =  pd.to_datetime(df['end_time'])
            df = df.set_index(['start_time','end_time'])
        
    elif r.status_code == 416:
        
        dfs = []
        while t1 < t2:
            
            t = t1 + relativedelta(months=+6)
            
            s1 = t1.strftime("%Y-%m-%dT%H:%M:%SZ")
            s2 = t.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        
            parameters = {'start_time': s1, \
                          'end_time': s2} 
            
               
            r = requests.get(url, params=parameters, headers=headers)
            
            t1 = t
            
            if r.status_code == 200:
                d = r.json()
                # Convert to dataframe
                if len(d)>0:
                    df = pd.DataFrame(d)
                    df['start_time'] =  pd.to_datetime(df['start_time'])
                    df['end_time'] =  pd.to_datetime(df['end_time'])
                    df = df.set_index(['start_time','end_time'])
                
                    dfs.append(df)
            
            else:
                print('API call issue')
                print('Status code:',r.status_code)
                return
        
        df = pd.concat(dfs)
        df = df[~df.index.duplicated(keep='first')] # Remove index dublicated times
        df = df[df.index.get_level_values(0).tz_localize(None) <= t2] # Remove rows with timestamp > t2
    
    else:
        print('API call issue')
        print('Status code:',r.status_code)
        return
                    
    return df


def get_open_data_latest(api_key, variable_id, api_version = 'v1'):


    ## Example
    # from fingridopendata import get_open_data_latest
    #
    # api_key = 'your_api_key'
    # variable_id = 265   
    #
    # d = get_open_data_latest(api_key, variable_id)
    
 
    url = 'https://api.fingrid.fi/{}/variable/{}/event/json'.format(api_version, variable_id)
    
    
    headers = {"x-api-key": api_key}
    
    print('Calling API ...')        
    r = requests.get(url, headers=headers)

    # r.url


    if r.status_code == 200:
        d = r.json() 
        # Convert to dataframe
        df = pd.DataFrame([d])
        df['start_time'] =  pd.to_datetime(df['start_time'])
        df['end_time'] =  pd.to_datetime(df['end_time'])
        df = df.set_index(['start_time','end_time'])       
    else:
        print('API call issue')
        print('Status code:',r.status_code)
        return
                    
    return df