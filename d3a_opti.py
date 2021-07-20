from pyomo.environ import AbstractModel,Set,Param,Var,Objective,Constraint,SolverFactory
from pyomo.environ import NonNegativeReals, inequality
from pyomo.environ import value



def initialize_model(model, model_data):

    model_instance = model.create_instance(model_data)

    return model_instance


def solve_model(model_instance):        
    optimizer = SolverFactory("glpk", executable="/usr/bin/glpsol")
    optimizer.solve(model_instance, tee=True, keepfiles=True)


    return model_instance



def d3a_opti():

    model = AbstractModel()

    ## SETS
    model.T = Set(dimen=1) # Periods
    model.H = Set(dimen=1) # Houses
    model.D = Set(dimen=1) # Loads
    model.B = Set(dimen=1) # Batteries
    model.G = Set(dimen=1) # Generators


    ## PARAMETERS
    model.demand                        = Param(model.T, model.D)
    model.generation                    = Param(model.T, model.G)
    model.battery_min_level             = Param(model.B, within=NonNegativeReals, default=0.0)
    model.battery_capacity              = Param(model.B, within=NonNegativeReals, default=0.0)
    model.battery_charge_max            = Param(model.B, within=NonNegativeReals, default=0.0)
    model.battery_discharge_max         = Param(model.B, within=NonNegativeReals, default=0.0)
    model.battery_efficiency_charge     = Param(model.B, within=NonNegativeReals, default=1.0)
    model.battery_efficiency_discharge  = Param(model.B, within=NonNegativeReals, default=1.0)
    model.bel_ini_level                 = Param(model.B, within=NonNegativeReals, default=0.0)
    model.marketmakerrate               = Param(model.T)
    model.feedintariff                  = Param(model.T)
    model.community_fee                 = Param(model.T)
    model.grid_fee                      = Param(model.T)
    model.carbon_emission               = Param(model.T)
    model.dt                            = Param()

    
    ## VARIABLES
    # Number of servings consumed of each food
    model.COST_ENERGY = Var(model.T)
    model.COST_GRID   = Var(model.T)
    model.PL1_BUY     = Var(model.T, model.H, within=NonNegativeReals)
    model.PL1_SELL    = Var(model.T, model.H, within=NonNegativeReals)
    model.PL2_BUY     = Var(model.T, within=NonNegativeReals)
    model.PL2_SELL    = Var(model.T, within=NonNegativeReals)    
    model.BEL         = Var(model.T, model.B, within=NonNegativeReals)
    model.B_IN        = Var(model.T, model.B, within=NonNegativeReals)
    model.B_OUT       = Var(model.T, model.B, within=NonNegativeReals)
    model.CO2         = Var(model.T)


    ## OBJECTIVE
    # Minimize cost
    def total_cost(model):
        return sum(model.COST_ENERGY[t] + model.COST_GRID[t] for t in model.T)
    model.total_cost = Objective(rule=total_cost)


    ## VARIABLE LIMITS
    def soc_limits(model, t, b):
        return inequality(model.battery_min_level[b], model.BEL[t,b], model.battery_capacity[b])
    model.soc_limits = Constraint(model.T, model.B, rule=soc_limits)

    def charge_limits(model, t, b):
        return inequality(0.0, model.B_IN[t,b], model.battery_charge_max[b])
    model.charge_limits = Constraint(model.T, model.B, rule=charge_limits)

    def discharge_limits(model, t, b):
        return inequality(0.0, model.B_OUT[t,b], model.battery_discharge_max[b])
    model.discharge_limits = Constraint(model.T, model.B, rule=discharge_limits)    


    ## CONSTRAINTS
    # Total energy cost per period  
    def energy_cost(model, t):
        return model.COST_ENERGY[t] == model.marketmakerrate[t]*model.PL2_BUY[t]*model.dt - model.feedintariff[t]*model.PL2_SELL[t]*model.dt
    model.energy_cost = Constraint(model.T, rule=energy_cost)    
    
    # Total grid cost per period
    def grid_cost(model, t):
        return model.COST_GRID[t] ==  sum( model.community_fee[t]*model.PL1_BUY[t,h]*model.dt for h in model.H ) \
                                + model.grid_fee[t]*model.PL2_BUY[t]*model.dt \
                                + (model.grid_fee[t]+model.community_fee[t])*model.PL2_SELL[t]*model.dt
    model.grid_cost = Constraint(model.T, rule=grid_cost)     
        
    
    # Community energy balance
    def energy_balance_grid(model, t):
        return model.PL2_SELL[t] - model.PL2_BUY[t] == sum( model.PL1_SELL[t,h] - model.PL1_BUY[t,h] for h in model.H )
    model.energy_balance_grid = Constraint(model.T, rule=energy_balance_grid)    
    
    # House energy balance
    def energy_balance_house(model, t, h):
        return model.PL1_SELL[t,h] - model.PL1_BUY[t,h] \
            == sum(model.generation[t,i] for i in [h] if h in model.G) \
            + sum(model.B_OUT[t,i] - model.B_IN[t,i] for i in [h] if h in model.B) \
            - sum(model.demand[t,i] for i in [h] if h in model.D)
    model.energy_balance_house = Constraint(model.T, model.H, rule=energy_balance_house)    

    # Battery energy balance
    def battery_soc(model, t, b):
        if t==1:
            return model.BEL[t,b] - model.bel_ini_level[b] == model.battery_efficiency_charge[b]*model.B_IN[t,b]*model.dt  - (1/model.battery_efficiency_discharge[b])*model.B_OUT[t,b]*model.dt
        else:
            return model.BEL[t,b] - model.BEL[t-1,b] == model.battery_efficiency_charge[b]*model.B_IN[t,b]*model.dt  - (1/model.battery_efficiency_discharge[b])*model.B_OUT[t,b]*model.dt
    model.battery_soc = Constraint(model.T, model.B, rule=battery_soc) 
    
    
    # Community CO2 emissions
    def carbon_emissions(model, t):
        return model.CO2[t] == (model.PL2_BUY[t] - model.PL2_SELL[t])*model.carbon_emission[t]*model.dt
    model.carbon_emissions = Constraint(model.T, rule=carbon_emissions)    
    

    return model



def d3a_opti_solution(solution):
    
    s = dict()
    s['members'] = solution.H.data()
    
    s['cost_energy'] = value(solution.COST_ENERGY[:])
    s['cost_grid'] = value(solution.COST_GRID[:])
    
    s['power_buy_community'] = value(solution.PL2_BUY[:])
    s['power_sell_community'] = value(solution.PL2_SELL[:])
    
    s['power_buy_member'] = {}
    s['power_sell_member'] = {}
    for m in s['members']:
        s['power_buy_member'][m] = value(solution.PL1_BUY[:,m])
        s['power_sell_member'][m] = value(solution.PL1_SELL[:,m])
    
    
    s['battery_soc_member'] = {}
    s['battery_charge_member'] = {}
    s['battery_discharge_member'] = {}
    for b in solution.B.data():
        s['battery_soc_member'][b] = value(solution.BEL[:,b])
        s['battery_charge_member'][b] = value(solution.B_IN[:,b])
        s['battery_discharge_member'][b] = value(solution.B_OUT[:,b])
    
    s['carbon_emissions'] = value(solution.CO2[:])

    return s