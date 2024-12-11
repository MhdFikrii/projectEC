import streamlit as st
from dataclasses import dataclass
from typing import List

@dataclass
class Program:
    name: str
    ratings: List[float]

def read_csv_to_dict(file_path: str) -> dict:
    """
    Reads a CSV file and converts it to a dictionary.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionary containing program names as keys and lists of ratings as values.
    """
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            programs = {}
            for row in reader:
                program_name = row[0]
                ratings = [float(x) for x in row[1:]]
                programs[program_name] = ratings

    except FileNotFoundError:
        st.error("The file was not found.")
        return None

def main():
    # Initialize parameters with default values
    co_r = 0.8
    mut_r = 0.2

    # Set up Streamlit interface for parameter input
    if "co_r" not in st.session_state:
        st.session_state.co_r = co_r
    if "mut_r" not in st.session_state:
        st.session_state.mut_r = mut_r

    col1, col2, col3 = st.columns(3)

    with col1:
        # Crossover rate input
        st.header("Crossover Rate")
        co_r_input = st.number_input("Enter crossover rate (0-0.95):", value=co_r, min_value=0,
max_value=0.95)
        if co_r_input < 0 or co_r_input > 0.95:
            st.error("Invalid input: crossover rate must be between 0 and 0.95.")

    with col2:
        # Mutation rate input
        st.header("Mutation Rate")
        mut_r_input = st.number_input("Enter mutation rate (0.01-0.05):", value=mut_r, min_value=0.01,
max_value=0.05)
        if mut_r_input < 0.01 or mut_r_input > 0.05:
            st.error("Invalid input: mutation rate must be between 0.01 and 0.05.")

    # Display the updated parameters
    col4 = st.columns(1)
    with col4:
        st.header("Updated Parameters")
        st.write(f"Crossover Rate: {st.session_state.co_r}")
        st.write(f"Mutation Rate: {st.session_state.mut_r}")

if __name__ == "__main__":
    main()
