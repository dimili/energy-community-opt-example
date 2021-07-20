import pandas as pd
from pandas.tseries.frequencies import to_offset
import numpy as np


def d3a_opti_input(data):    
    
    loc_names = list(data.keys())


    prd = data[loc_names[0]]['timestamps']
    
    periods = np.arange(1, len(prd)+1)
    resolution = {None: pd.to_timedelta(to_offset(pd.infer_freq(prd))).total_seconds()/3600}

    
    market_maker_rate  = dict(zip(periods, data[loc_names[0]]['market maker rate']))
    feed_in_tariff = dict(zip(periods, data[loc_names[0]]['feed in tariff']))
    community_fee =  dict(zip(periods, data[loc_names[0]]['community fee']))
    grid_fee = dict(zip(periods, data[loc_names[0]]['grid fee']))
    carbon_emission_factor = dict(zip(periods, data[loc_names[0]]['carbon emission factor']))
    
    demand = dict()
    generation = dict()
    
    battery_min_level = dict()
    battery_capacity = dict()
    battery_charge_max = dict()
    battery_discharge_max = dict()
    battery_efficiency_charge = dict()
    battery_efficiency_discharge = dict()
    bel_ini_level = dict()
    bel_fin_level = dict()
    
    
    for loc_name in loc_names:
        nm = loc_name
        
        keys = list(zip(periods, [nm]*len(periods)))
        
        d = dict(zip(keys, data[loc_name]['demand']))
        demand.update(d)
        
        d = dict(zip(keys, data[loc_name]['generation']))
        generation.update(d)
        
        
        battery_min_level.update({nm: data[loc_name]['battery']['min soc']})
        battery_capacity.update({nm: data[loc_name]['battery']['capacity']})
        battery_charge_max.update({nm: data[loc_name]['battery']['charging power']})
        battery_discharge_max.update({nm: data[loc_name]['battery']['discharging power']})
        battery_efficiency_charge.update({nm: data[loc_name]['battery']['charging efficiency']})
        battery_efficiency_discharge.update({nm: data[loc_name]['battery']['discharging efficiency']})
        
    
        bel_ini_level.update({nm: data[loc_name]['battery']['min soc']})
        bel_fin_level.update({nm: data[loc_name]['battery']['min soc']})


    # Create sets
    demand_members = {b for a, b in list(demand.keys())}
    generation_members = {b for a, b in list(generation.keys())}
    battery_members = battery_capacity.keys()
    all_members = demand_members | generation_members | battery_members
    
    demand_members = list(demand_members)
    generation_members = list(generation_members)
    battery_members = list(battery_members)
    all_members = list(all_members)
    

    # Create model data input dictionary
    model_data = {None: {
        'T': periods,
        'H': all_members,
        'D': demand_members,
        'G': generation_members,
        'B': battery_members,

        
        'generation': generation,
        'demand': demand,
        
        'battery_min_level': battery_min_level,
        'battery_capacity': battery_capacity,
        'battery_charge_max': battery_charge_max,
        'battery_discharge_max': battery_discharge_max,
        'battery_efficiency_charge': battery_efficiency_charge,
        'battery_efficiency_discharge': battery_efficiency_discharge,
        'bel_ini_level': bel_ini_level,
        'bel_fin_level': bel_fin_level,
        
        'marketmakerrate': market_maker_rate,
        'feedintariff': feed_in_tariff,
        'community_fee': community_fee,
        'grid_fee': grid_fee,
        
        'carbon_emission': carbon_emission_factor,
        
        'dt': resolution,
    }}  

    return model_data