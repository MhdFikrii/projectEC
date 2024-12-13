import csv
import random
import streamlit as st
import pandas as pd

# Function to read the CSV file and convert it to the desired format
def read_csv_to_dict(file_path):
    program_ratings = {}
    
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        # Skip the header
        header = next(reader)
        
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]  # Convert the ratings to floats
            program_ratings[program] = ratings
    
    return program_ratings

# Path to the CSV file
file_path = 'pages/program_ratings.csv'

# Get the data in the required format
program_ratings_dict = read_csv_to_dict(file_path)

##################################### USER INPUT PARAMETERS ###############################################

st.title("TV Scheduling with Genetic Algorithm")

st.sidebar.header("Genetic Algorithm Parameters")

# Allow user to input and adjust parameters dynamically
CO_R = st.sidebar.slider("Crossover Rate (CO_R):", min_value=0.0, max_value=0.95, value=0.8, step=0.01, key="crossover_rate")
MUT_R = st.sidebar.slider("Mutation Rate (MUT_R):", min_value=0.01, max_value=0.05, value=0.02, step=0.01, key="mutation_rate")

GEN = st.sidebar.number_input("Number of Generations (GEN):", min_value=10, max_value=500, value=100, step=10, key="generations")
POP = st.sidebar.number_input("Population Size (POP):", min_value=10, max_value=200, value=50, step=10, key="population_size")
EL_S = st.sidebar.number_input("Elitism Size (EL_S):", min_value=1, max_value=10, value=2, step=1, key="elitism_size")

# Display selected parameters
st.sidebar.write(f"Selected Crossover Rate: {CO_R}")
st.sidebar.write(f"Selected Mutation Rate: {MUT_R}")
st.sidebar.write(f"Number of Generations: {GEN}")
st.sidebar.write(f"Population Size: {POP}")
st.sidebar.write(f"Elitism Size: {EL_S}")

##################################### DEFINING PARAMETERS AND DATASET ################################################################
ratings = program_ratings_dict

all_programs = list(ratings.keys())  # All programs
all_time_slots = list(range(6, 24))  # Time slots (6 AM to 11 PM)

######################################### DEFINING FUNCTIONS ########################################################################
# Fitness function
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

# Population initialization
def initialize_pop(programs, time_slots):
    if not programs:
        return [[]]

    all_schedules = []
    for i in range(len(programs)):
        for schedule in initialize_pop(programs[:i] + programs[i + 1:], time_slots):
            all_schedules.append([programs[i]] + schedule)

    return all_schedules

# Brute-force search for the initial best schedule
def finding_best_schedule(all_schedules):
    best_schedule = []
    max_ratings = 0

    for schedule in all_schedules:
        total_ratings = fitness_function(schedule)
        if total_ratings > max_ratings:
            max_ratings = total_ratings
            best_schedule = schedule

    return best_schedule

# Crossover function
def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

# Mutation function
def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

# Genetic algorithm
def genetic_algorithm(initial_schedule, generations, population_size, crossover_rate, mutation_rate, elitism_size):
    population = [initial_schedule]

    # Initialize population
    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    # Evolve over generations
    for generation in range(generations):
        new_population = []

        # Elitism
        population.sort(key=lambda schedule: fitness_function(schedule), reverse=True)
        new_population.extend(population[:elitism_size])

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.extend([child1, child2])

        population = new_population

    return population[0]

##################################################### RESULTS ###################################################################################

# Generate all possible schedules (brute force)
all_possible_schedules = initialize_pop(all_programs, all_time_slots)

# Brute force schedule
initial_best_schedule = finding_best_schedule(all_possible_schedules)

# Genetic algorithm schedule
genetic_schedule = genetic_algorithm(
    initial_best_schedule,
    generations=GEN,
    population_size=POP,
    crossover_rate=CO_R,
    mutation_rate=MUT_R,
    elitism_size=EL_S,
)

# Create the final schedule
final_schedule_data = {
    "Time Slot": [f"{all_time_slots[time_slot]:02d}:00" for time_slot in range(len(genetic_schedule))],
    "Program": genetic_schedule,
    "Rating": [ratings[program][time_slot] for time_slot, program in enumerate(genetic_schedule)],
}

df = pd.DataFrame(final_schedule_data)

# Display the final results
st.write("### Final Optimal Schedule:")
st.table(df)

# Display the total ratings
st.write("### Total Ratings:", fitness_function(genetic_schedule))
