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

