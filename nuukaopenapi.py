# https://helsinki-openapi.nuuka.cloud/swagger/index.html

import requests
import pandas as pd
    

def get_property_list(api_version = 'v2.0'):
        
    ## Example
    # from nuukaopenapi import get_property_list
    #
    # prop_list = get_property_list()   
        

    url = 'https://helsinki-openapi.nuuka.cloud/api/{}/Property/List'.format(api_version)

    
    print('Getting property list ...')        
    r = requests.get(url)

    # r.url


    if r.status_code == 200:
        d = r.json()
        df = pd.DataFrame(d)
    
    else:
        print('API call issue')
        print('Status code:',r.status_code)
        return
                    
    return df
    


def searh_property(search_string, search_record = 'LocationName', api_version = 'v2.0'):
    

    ## Example
    # from nuukaopenapi import searh_property
    # 
    # search_string = '1000 Hakaniemen kauppahalli'
    # search_record = 'LocationName'/'PropertyCode'/'BuildingType'/'PurposeOfUse'/'BuildingCode'
    # prop_metadata = searh_property(search_string, search_record)     



    url = 'https://helsinki-openapi.nuuka.cloud/api/{}/Property/Search'.format(api_version)


    parameters = {'SearchString': search_string, \
                  'SearchFromRecord': search_record} 
    
    print('Generating API token ...')        
    r = requests.get(url, params=parameters)

    if r.status_code == 200:
        d = r.json()
    
    else:
        print('API call issue')
        print('Status code:',r.status_code)
        return
                    
    return d



def searh_property_df(search_string, search_record = 'LocationName', api_version = 'v2.0'):
   
    
    ## Example
    # from nuukaopenapi import searh_property_df
    # 
    # search_string = '1000 Hakaniemen kauppahalli'
    # search_record = 'LocationName'/'PropertyCode'/'BuildingType'/'PurposeOfUse'/'BuildingCode'
    # prop_metadata = searh_property_df(search_string, search_record)     

 
    d = searh_property(search_string, search_record, api_version)  



    df = []
    for i in range(0,len(d)):

        d[i]['buildings'] = d[i]['buildings'][0]['buildingCode']
        d[i]['buildingCode'] = d[i].pop('buildings')
    
        reportinggroup = []
        for j in range(0,len(d[i]['reportingGroups'])):
        
            rg = d[i]['reportingGroups'][j]['name']
        
            reportinggroup.append(rg)

        d[i]['reportingGroups'] = [', '.join(reportinggroup)] 
    

        dfi = pd.DataFrame(d[i])
        df.append(dfi)

    df = pd.concat(df, axis=0)
    
    return df



def get_property_data(search_string, reporting_group, start_time, end_time, time_group = 'hourly', search_record = 'LocationName', api_version = 'v2.0'):
    
    ## Example
    # from nuukaopenapi get_property_data
    # 
    # search_string = '1000 Hakaniemen kauppahalli'
    # reporting_group = 'Electricity'/'Heat'/'Water'/'DistrictCooling'
    # start_time =  'yyyy-MM-dd HH:mm'
    # end_time =  'yyyy-MM-dd HH:mm'
    # time_group = 'hourly'/'daily'/'monthly'
    # search_record = 'LocationName'/'PropertyCode'/'BuildingType'/'PurposeOfUse'/'BuildingCode'
    # data = get_property_data(search_string, reporting_group, start_time, end_time, time_group = time_group, search_record = search_record)     


   
    url = 'https://helsinki-openapi.nuuka.cloud/api/{}/EnergyData/{}/ListByProperty'.format(api_version, time_group)


    parameters = {'SearchString': search_string, \
                  'Record': search_record, \
                  'ReportingGroup': reporting_group, \
                  'StartTime': start_time, \
                  'EndTime': end_time} 
    
    print('Generating property data ...')        
    r = requests.get(url, params=parameters)

    if r.status_code == 200:
        d = r.json()
        df = pd.DataFrame(d).set_index('timestamp')
        df.index = pd.to_datetime(df.index)
        df = get_local_timeindex(df)
    
    else:
        print('API call issue')
        print('Status code:',r.status_code)
        return
                    
    return df



def get_local_timeindex(df):
    
    # Nuuka data time is local time in Helsinki
    # The spring daylight saving hour (03:00 on last Sunday of March) is correctly missing
    # The fall daylight saving hour (03:00 on last Sunday of October) however is not dublicate as it should be
    # Instead there is only one timestamp that contains the aggregated quantity of the dublicate hours
    # This stript infers the local time fixing the issue above 
    
    # Get local time index which has 'NaT' in the ambiguous rows
    indx = df.index.tz_localize(tz='Europe/Helsinki', ambiguous='NaT', nonexistent='raise')


    # Devide ambiguous rows by two to get the single hour quantity
    df.loc[indx.isnull(),'value'] = df.loc[indx.isnull(),'value']/2
    
    # Dublicate ambiguous rows
    df = df.reset_index()
    dslice = df.iloc[indx.isnull(),:]
    dslice.index = dslice.index+0.5
    df = df.append(dslice, ignore_index=False)
    df = df.sort_index().reset_index(drop=True)
    df = df.set_index('timestamp')
    
    # Change dataframe index to local time and infer ambiguous rows
    df.index = df.index.tz_localize(tz='Europe/Helsinki', ambiguous='infer', nonexistent='raise')

    return df

