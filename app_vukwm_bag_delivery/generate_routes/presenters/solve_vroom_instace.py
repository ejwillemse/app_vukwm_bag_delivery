import streamlit as st


def solve():
    problem_instance = st.session_state.data_04_model_input["vroom_input"]
    solution = problem_instance.solve(exploration_level=5, nb_threads=4)
    st.write(solution.summary.cost)
    st.write(solution.unassigned)
    st.write(solution.routes)
    return solution
