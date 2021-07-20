import requests
import pandas as pd 


def get_pv_generation_data(parameters):
    
    # Parameter value range
    # latitude: -90 to 90
    # longitude: -180 to 180
    # capacity_kw: > 0
    # azimuth: 0 to 360
    # tilt: 0 to 90
    # start_date > 1979
    # end_date < present
    
    
    ## Example
    # from energydatamap import get_pv_generation_data
    # parameters = {'longitude': 7, 'latitude': 51, 'capacity_kw': 1200, \
    #         'azimuth': 170, 'tilt': 10,'start_date': '2020-01-01',\
    #         'end_date': '2020-01-31','frequency': '15min'}    
    
    # df = get_pv_generation_data(parameters)
    

    url = 'https://energydatamap.com/api/solar'            
    
    print('Calling API for data generation')        
    r = requests.get(url, params=parameters)


    if r.status_code == 200:
        d = r.json()
        # Convert to dataframe
        df = pd.DataFrame(d).set_index('valid_datetime')
        df.index = pd.to_datetime(df.index)
    else:
        print('API problem in data generation')
        print('Status code:',r.status_code)
        return
                    
    return df