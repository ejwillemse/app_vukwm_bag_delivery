import streamlit as st


def solve():
    problem_instance = st.session_state.data_04_model_input["vroom_input"]
    solution = problem_instance.solve(exploration_level=5, nb_threads=4)

    st.session_state.data_06_model_output = {"vroom_solution": solution}
