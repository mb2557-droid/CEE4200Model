'''
This is a script that stores all of the data for each reservoir and runs the model

12/3/2025
Matt Burgos mb2557
Rachel Pyeon rp653
'''

from funcs import *

# Constants
demand = 1000 * 0.40 #MGD, assume largest proportion (40% of total demand)

max_capacity_schoharie = 17600 #MG
min_capacity_schoharie = 0.405*max_capacity_schoharie # MG
starting_capacity_schoharie = 0.855*max_capacity_schoharie # MG

max_capacity_ashokan = 122900 #MG
min_capacity_ashokan = 0.696*max_capacity_ashokan #MG
starting_capacity_ashokan = 0.792*max_capacity_ashokan #MG

schoharie_flows, ashokan_flows, times = load_data()



# Example control policy and results 
release_points_schoharie = [229.56, 400.01, 402.27] # These are the different values of r
release_points_ashokan = [210.38, 226.57, 455.68]

plot_control_policy2(release_points_schoharie, max_capacity_schoharie, reservoir = "Schoharie")
plot_control_policy2(release_points_ashokan, max_capacity_ashokan, reservoir = "Ashokan")

plot_storage_over_time2(schoharie_flows, demand, release_points_schoharie, starting_capacity_schoharie, 
                        min_capacity_schoharie, max_capacity_schoharie, reservoir = "Schoharie")
plot_storage_over_time2(ashokan_flows, demand, release_points_ashokan, starting_capacity_ashokan, 
                        min_capacity_schoharie, max_capacity_ashokan, reservoir = "Ashokan")

plot_discharge_over_time2(schoharie_flows, demand, release_points_schoharie, starting_capacity_schoharie, 
                          min_capacity_schoharie, max_capacity_schoharie, reservoir = "Schoharie")
plot_discharge_over_time2(ashokan_flows, demand, release_points_ashokan, starting_capacity_ashokan, 
                          min_capacity_schoharie, max_capacity_ashokan, reservoir = "Ashokan")



# OPTIMIZATION

data_schoharie = {
    'daily_flows': schoharie_flows,
    'demand': demand,
    'v_start': starting_capacity_schoharie,
    'v_min': min_capacity_schoharie,
    'v_max': max_capacity_schoharie,
    'optimizing': True
}

data_ashokan = {
    'daily_flows': ashokan_flows,
    'demand': demand,
    'v_start': starting_capacity_ashokan,
    'v_min': min_capacity_ashokan,
    'v_max': max_capacity_ashokan,
    'optimizing': True
}

# Choose number of decision variables and population size
num_decisions = 3
pop_size = 400
plot_pareto(num_decisions, pop_size, data_schoharie, reservoir="Schoharie")
plot_pareto(num_decisions, pop_size, data_ashokan, reservoir="Ashokan")
