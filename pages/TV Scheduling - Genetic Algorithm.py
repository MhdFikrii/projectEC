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

# Allow user to input Crossover Rate (CO_R) and Mutation Rate (MUT_R)
CO_R = st.sidebar.slider("Crossover Rate (CO_R):", min_value=0.0, max_value=0.95, value=0.8, step=0.01, key="crossover_rate")
MUT_R = st.sidebar.slider("Mutation Rate (MUT_R):", min_value=0.01, max_value=0.05, value=0.02, step=0.01, key="mutation_rate")

# Display parameters
st.sidebar.write(f"Selected Crossover Rate: {CO_R}")
st.sidebar.write(f"Selected Mutation Rate: {MUT_R}")

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

# Mutation function with validation
def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    while new_program == schedule[mutation_point]:  # Avoid same program mutation
        new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

# Crossover function with validation
def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)  # Ensure valid range
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]

    # Ensure unique schedules (optional, depending on problem constraints)
    if len(set(child1)) != len(schedule1):
        child1 = schedule1.copy()  # Use parent if invalid
    if len(set(child2)) != len(schedule2):
        child2 = schedule2.copy()

    return child1, child2

# Population initialization
def initialize_population(programs, time_slots):
    population = []
    for _ in range(50):  # Fixed population size of 50
        random_schedule = programs.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule[:len(time_slots)])
    return population

# Genetic algorithm
def genetic_algorithm(initial_population, generations=100, crossover_rate=CO_R, mutation_rate=MUT_R):
    population = initial_population

    for generation in range(generations):
        # Sort population by fitness (descending)
        population.sort(key=lambda schedule: fitness_function(schedule), reverse=True)
        next_generation = population[:2]  # Elitism: retain top 2 schedules

        # Generate new population
        while len(next_generation) < len(population):
            parent1, parent2 = random.choices(population[:10], k=2)  # Select parents from top 10

            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)

            next_generation.extend([child1, child2])

        population = next_generation[:len(population)]  # Maintain population size

    # Return the best schedule
    return max(population, key=fitness_function)

############################################# RESULTS ###################################################################################

# Initialize population
initial_population = initialize_population(all_programs, all_time_slots)

# Run the genetic algorithm
genetic_schedule = genetic_algorithm(initial_population)

# Create a DataFrame for the final schedule
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
