# Tasks

This file tracks all work for the E-Commerce Analytics dashboard.

## Definition of Done

- Acceptance criteria for the milestone are met
- App runs locally with `streamlit run app.py`
- Changes committed with the milestone ID in the commit message

## To Do

### TASK-7: Deployment to Streamlit Community Cloud
Deploy the dashboard to a publicly accessible URL (NFR-5).
- [ ] App deployed to Streamlit Community Cloud
- [ ] Public URL verified to load and render correctly

Commit:

## In Progress

## Done

### TASK-6: Testing and refinement
Verify the dashboard against the PRD's acceptance criteria and polish appearance.
- [x] All values match expected calculations from the CSV
- [x] Dashboard runs with no errors or warnings and loads within 5 seconds
- [x] Layout and labels are clear and presentation-ready

Commit: 91f7c2f
Notes: clean

### TASK-5: Category and region breakdowns
Add bar charts for sales by category and by region, sorted by value (FR-3, FR-4).
- [x] Category bar chart shows all 5 categories sorted highest to lowest
- [x] Region bar chart shows all 4 regions sorted highest to lowest
- [x] Both charts have interactive tooltips with exact values
- [x] **Extra feature, personal brainstorming (beyond PRD scope):** Top 5 Products table by total revenue, with units sold

Commit: 71659ca
Notes: clean

### TASK-4: Sales trend chart
Add a line chart showing sales over time (FR-2).
- [x] Line chart plots sales by date with time on the X-axis
- [x] Interactive tooltips show exact values on hover

Commit: 11db7bf
Notes: clean

### TASK-3: KPI cards implementation
Display Total Sales and Total Orders as KPI cards (FR-1).
- [x] Total Sales shown formatted as currency (~$116,500 expected)
- [x] Total Orders shown as a formatted count (482 expected)

Commit: 714dbff
Notes: clean

### TASK-2: Data loading and basic structure
Load `data/sales-data.csv` into a Pandas DataFrame and validate its structure.
- [x] CSV loads with correct column types (date, numeric, categorical)
- [x] Loaded row count matches the 482 transaction records
- [x] Basic error handling for missing/malformed file

Commit: 9f4b48b
Notes: clean

### TASK-1: Environment setup and project initialization
Set up the Python project structure and dependencies for the Streamlit app.
- [x] `requirements.txt` includes Streamlit, Plotly, and Pandas
- [x] Project folder structure created (e.g. `app.py`, `data/`)
- [x] `streamlit run app.py` launches a blank/placeholder app without errors

Commit: 8d425c7
Notes: clean
