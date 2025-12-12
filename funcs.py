'''
This file stores all of the functions used for our model

12/12/2025
Matt Burgos mb2557
Rachel Pyeon rp653
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import mplcursors
from platypus import NSGAII, Problem, Real


def load_data():
    '''
    Returns
    1. Daily flow for Schoharie in MGD
    2. Daily flow for Ashokan in MGD
    3. Corresponding days
    '''
    # Load all data
    df = pd.read_csv('Schoharie_Creek_at_Gilboa_Bridge.csv')
    gilboa_bridge = df.iloc[:, 1]
    gilboa_bridge = gilboa_bridge.tolist()

    df = pd.read_csv('Manor_Kill_at_West_Conesville_near_Gilboa.csv')
    manor_kill = df.iloc[:, 1]
    manor_kill = manor_kill.tolist()

    df = pd.read_csv('Schoharie_Creek_at_Prattsville.csv')
    prattsville = df.iloc[:, 1]
    prattsville = prattsville.tolist()

    df = pd.read_csv('Esopus_Creek_at_Cold_Brook.csv')
    esopus_creek = df.iloc[:, 1]
    esopus_creek = esopus_creek.tolist()

    days = df.iloc[:, 0]
    days = days.tolist()

    # Convert from m^3/s to MGD
    all_data = [gilboa_bridge, manor_kill, prattsville, esopus_creek]
    for i in range(len(all_data)):
        for j in range(len(all_data[i])):
            all_data[i][j] = all_data[i][j]*22.8245

    # Calculate total inflow into schoharie
    schoharie_total = []
    for i in range(len(gilboa_bridge)):
        schoharie_total.append(gilboa_bridge[i] + manor_kill[i] + prattsville[i])

    return schoharie_total, esopus_creek, days


def calculate_control_policy2(release_points, v_max):
    '''
    Returns
    1. The volume of the reservoir
    2. The corresponding dischage for each volume

    Parameters
    release_points: list of release points
    v_max: max volume of reservoir
    '''
    # Add the points (0,0) and (v_max, 600)
    release_points.insert(0, 0)
    release_points.append(600)

    volumes = np.linspace(0, v_max+v_max/5, 1000)
    discharges = [0]*len(volumes)
    volume_points = np.linspace(0, v_max, len(release_points))

    for i in range(len(volumes)):
        # Case if volume is greater than max
        if volumes[i] >= v_max:
            discharges[i] = 600
        # Otherwise
        else:
            for j in range(len(release_points)):
                if volume_points[j] <= volumes[i] <= volume_points[j+1]:
                    discharges[i] = release_points[j] + (volumes[i]-volume_points[j]) * \
                        (release_points[j+1]-release_points[j]) / (volume_points[j+1] - volume_points[j])

    return volumes, discharges


def plot_control_policy2(release_points, v_max, reservoir):
    '''
    Plots the control policy for a reservoir

    Parameters:
    release_points: list of release points
    v_max: max volume of reservoir
    reservoir: string of name of the reservoir
    '''
    v,d = calculate_control_policy2(release_points, v_max)
    plt.plot(v, d)
    plt.xlabel('Reservoir volume (million gallons)')
    plt.ylabel('Discharge (MGD)')
    plt.title(f'Control Policy for the {reservoir} Reservoir')
    plt.show()


def get_storage_and_discharge2(daily_flows, demand, release_points, v_start, v_min, v_max, optimizing=False):
    '''
    If optimizing == False, returns
    1. Reservoir storage every day
    2. Reservoir discharge every day
    
    If optimizing == True, returns
    1. list of values with the 3 indicators
    '''
    reservoir_storage, reservoir_discharge = [0]*len(daily_flows), [0]*len(daily_flows)
    reservoir_storage[0] = v_start
    reservoir_discharge[0] = demand
    demand_deficit = 0
    dead_storage_deficit = 0 
    mef_violations = 0
    volume_points = np.linspace(0, v_max, len(release_points))

    for i in range(len(daily_flows)-1):
        # Case if volume is greater than max
        if reservoir_storage[i]+daily_flows[i] >= v_max:
            discharge = 600
        # Otherwise
        else:
            for j in range(len(release_points)-1):
                if volume_points[j] <= reservoir_storage[i]+daily_flows[i] <= volume_points[j+1]:
                    discharge = release_points[j] + (reservoir_storage[i]+daily_flows[i]-volume_points[j]) * \
                        (release_points[j+1]-release_points[j]) / (volume_points[j+1] - volume_points[j])

        # Calculate demand deficit
        if discharge < demand:
            demand_deficit += demand-discharge

        # Calculate minimum enviornmental flow violations
        if discharge < 15:
            mef_violations += 1

        # Update storage and discharge at t+1
        reservoir_discharge[i+1] = discharge
        reservoir_storage[i+1] = reservoir_storage[i] + daily_flows[i] - discharge

        # Calculate dead storage deficit
        if reservoir_storage[i+1] < v_min:
            dead_storage_deficit += v_min-reservoir_storage[i+1]

        # Do not go above capacity
        if reservoir_storage[i+1] > v_max:
            reservoir_storage[i+1] = v_max

    indicators = {
        'Average daily deficit on demand': demand_deficit/len(daily_flows),
        'Average daily deficit on dead storage': dead_storage_deficit/len(daily_flows),
        'Average annual minimum flow violations': mef_violations/len(daily_flows)*365
    }

    if optimizing == True:
        return [indicators['Average daily deficit on demand'], indicators['Average daily deficit on dead storage'], 
                indicators['Average annual minimum flow violations']]

    return reservoir_storage, reservoir_discharge


def plot_storage_over_time2(daily_flows, demand, release_points, v_start, v_min, v_max, reservoir, optimizing=False):
    '''
    Plots the storage over time of a reservoir
    '''
    storage = get_storage_and_discharge2(daily_flows, demand, release_points, v_start, v_min, v_max, optimizing)[0]
    plt.plot(list(range(len(storage))), storage)
    plt.xlabel('Days since 1/1/1980')
    plt.ylabel('Storage (million gallons)')
    plt.title(f'Storage of {reservoir} Reservoir from 1/1/1980 to 1/31/2023')
    plt.show()


def plot_discharge_over_time2(daily_flows, demand, release_points, v_start, v_min, v_max, reservoir, optimizing=False):
    '''
    Plots the discharge over time of a reservoir with lines representing the minimum environmental flow
    '''
    discharge = get_storage_and_discharge2(daily_flows, demand, release_points, v_start, v_min, v_max, optimizing)[1]
    plt.plot(list(range(len(discharge))), discharge)
    plt.xlabel('Days since 1/1/1980')
    plt.ylabel('Discharge (MGD)')
    plt.title(f'Discharge of {reservoir} Reservoir from 1/1/1980 to 1/31/2023')
    # Create minimum flow lines
    x = np.arange(len((discharge)))
    day = x % 365
    y = np.ma.masked_where((day > 119) & (day < 304), np.full_like(x, 10))  # 10 MGD for Jan–Apr & Nov–Dec
    y2 = np.ma.masked_where((day < 120) | (day > 303), np.full_like(x, 15)) # 15 MGD for May–Oct
    plt.plot(x, y, 'r--', label='Minimum Discharge')
    plt.plot(x, y2, 'r--')
    plt.legend(loc='lower right', framealpha=1)
    plt.show()


# Define the optimization problem
class LakeOptimization(Problem):
    def __init__(self, num_points, data):
        # Create a problem with  decision variables and 3 objectives
        super(LakeOptimization, self).__init__(num_points, 3, num_points - 1)  # 4 decision variables, 3 objectives
        self.types[:] = [Real(0, 600) for _ in range(num_points)]
        self.constraints[:] = "<=0"
        self.data = data
    
    def evaluate(self, solution):
        # x = decision variables
        x = solution.variables

        for i in range(len(x) - 1):
            # Constraint is satisfied if x[i] ≤ x[i+1]
            solution.constraints[i] = x[i] - x[i+1]
        
        # If any constraint is violated, assign large penalty
        if any(c > 0 for c in solution.constraints):
            solution.objectives[:] = [1e6, 1e6, 1e6]
            return 
        
        # Calculate objectives based on decision variables x
        solution.objectives[:] = get_storage_and_discharge2(self.data['daily_flows'], self.data['demand'], 
                                                            x, self.data['v_start'], self.data['v_min'], 
                                                            self.data['v_max'], self.data['optimizing'])    


def plot_pareto(num_points, population_size, data, reservoir, return_data=False):
    '''
    Creates two plots
    1. Control policies for all pareto efficient solutions
    2. Pareto frontier (demand deficit vs dead storage deficit)
    '''
    # Run NSGA-II
    problem = LakeOptimization(num_points, data)
    algorithm = NSGAII(problem, population_size=population_size)
    algorithm.run(100)

    # Filter feasible solutions first (consecutive nodes must be increasing)
    penalty = 1e5 #penalty if not increasing
    feasible_solutions = [
        s for s in algorithm.result
        if all(obj < penalty for obj in s.objectives)
    ]
    if len(feasible_solutions) == 0:
        print("No feasible solutions.")
        return

    # Extract ONLY objective 1 and 2 for Pareto comparison
    obj12 = np.array([
        [float(s.objectives[0]), float(s.objectives[1])]
        for s in feasible_solutions
    ])

    def is_dominated(a, b):
        # b dominates a if:
        return (b[0] <= a[0] and b[1] <= a[1]) and (b[0] < a[0] or b[1] < a[1])

    pareto_mask = []
    for i in range(len(obj12)):
        a = obj12[i]
        dominated = False
        for j in range(len(obj12)):
            if i != j:
                b = obj12[j]
                if is_dominated(a, b):
                    dominated = True
                    break
        pareto_mask.append(not dominated)

    # Keep only nondominated solutions (based on the first 2 objectives)
    pareto_solutions = [s for s, keep in zip(feasible_solutions, pareto_mask) if keep]
    pareto_obj12 = obj12[pareto_mask]

    # Save front as data
    if return_data:
        pareto_vars = np.array([s.variables for s, keep in zip(feasible_solutions, pareto_mask) if keep])
        return pareto_obj12, pareto_vars
    
    # Plot control policy for nondominated feasible solutions
    for i, s in enumerate(pareto_solutions, start=1):
        v,d = calculate_control_policy2(list(s.variables), data["v_max"])
        plt.plot(v, d)
    plt.xlabel('Reservoir volume (million gallons)')
    plt.ylabel('Discharge (MGD)')
    plt.title(f'Pareto Efficient Control Policies for the {reservoir} Reservoir')
    plt.show()

    # Plot pareto frontier for nondominated feasible solutions
    plt.figure(figsize=(7,5))
    scatter = plt.scatter(pareto_obj12[:,0], pareto_obj12[:,1], marker='o')
    plt.xlabel("Average daily deficit on demand (MGD)")
    plt.ylabel("Average daily deficit on dead storage (MGD)")
    plt.title(f"Pareto Frontier for {reservoir} (Obj1 & Obj2 Only)")
    plt.grid(True)
    plt.tight_layout()

    # Tool so hovering cursor over points shows the release nodes
    cursor = mplcursors.cursor(scatter, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        i = sel.index
        sol = pareto_solutions[i]
        x_val, y_val = pareto_obj12[i]
        sel.annotation.set_text(
            f"({x_val:.3f}, {y_val:.3f})\n"
            f"release nodes = {np.round(sol.variables, 2)}"
        )

    plt.show()


def plot_uncertainty(front1, front2, front3, reservoir):
    plt.figure(figsize=(7,5))

    plt.scatter(front1[:,0], front1[:,1], label="40 years", s=40, color='blue')
    plt.scatter(front2[:,0], front2[:,1], label="First 20 years", s=40, color='red')
    plt.scatter(front3[:,0], front3[:,1], label="Second 20 years", s=40, color='green')

    plt.title(f"Uncertainty Analysis – {reservoir}\nPareto Fronts Comparison")
    plt.xlabel("Average daily deficit on demand (MGD)")
    plt.ylabel("Average daily deficit on dead storage (MGD)")
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()
