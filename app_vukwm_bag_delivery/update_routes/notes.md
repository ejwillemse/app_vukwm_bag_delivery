# Relevant sessions state objects

Assigned stops (stops to routes):

```python
assigned_stops = st.session_state.data_07_reporting["assigned_stops"]
```

Unassigned routes:

```python
unassigned_routes = st.session_state.data_02_intermediate["unassigned_routes"]
```

Unused routes

```python
unused_routes = st.session_state.data_07_reporting["unused_routes"]
```

Unserviced stops

```python
unserviced_stops = st.session_state.data_07_reporting["unserviced_stops"]
```

Locations

```python
locations = st.session_state.data_03_primary["locations"]
```

For routing

```
unassigned_routes = st.session_state.data_03_primary["unassigned_routes"]
```

```
unassigned_stops = st.session_state.data_03_primary["unassigned_stops"]
```

And then just filter

Changes required when edits are saved...

Just retrieved:

```
st.session_state.data_02_intermediate["unassigned_routes"]
st.session_state.data_02_intermediate["unassigned_stops"]
```

To be updated:

process_assigned_data

```
st.session_state.data_07_reporting["unused_routes"]
st.session_state.data_07_reporting["unserviced_stops"]
st.session_state.data_07_reporting["assigned_stops"]
```

create_routing_object

Used

```
st.session_state.data_02_intermediate["unassigned_stops"]
st.session_state.data_04_model_input["matrix"]
st.session_state.data_03_primary["locations"]
st.session_state.data_03_primary["unassigned_stops"]
```

To be updated:

```
st.session_state.data_03_primary["unassigned_routes"]
```
