# Volt Guard Buddy (Streamlit + Excel)

This app replaces the original FastAPI + React + PostgreSQL stack with Streamlit + Python + Excel while preserving core functionality.

## Run

- Windows PowerShell:
  - Create venv: `py -m venv venv`
  - Install deps: `./venv/Scripts/python.exe -m pip install streamlit pandas openpyxl numpy plotly matplotlib`
  - Start app: `./venv/Scripts/streamlit.exe run volt_guard_buddy_streamlit/app.py`

## Data Files

- `data/batteries.xlsx`: columns `id, product_number, current_voltage, last_checked_date, packing_month, status, total_checks`
- `data/stakeholders.xlsx`: columns `id, name, email`
- `data/battery_checks.xlsx`: columns `id, battery_id, voltage_reading, voltage_during_check, checked_by, notes, checked_at`

## Feature Tracking

| Component | Action | Condition | Output | Notes |
|---|---|---|---|---|
| Scanner input | Scan / Find Battery | Input not empty | Shows battery details if found | Warns if not found |
| Add Battery | Submit | Product Number required | Adds battery to Excel | Optional initial voltage |
| Dashboard KPIs | View | N/A | Total, Active, Low, Need Charging | Styled KPI cards |
| Inventory table | Filter | Status, product contains, voltage range | Filters rows | Styled badges, days since check, export CSV |
| Update Voltage | Submit | Requires ID, voltage, checked_by | Updates voltage, increments total_checks, appends check | Dialog-like form; live status badge |
| Delete Battery | Click | Confirm checked | Deletes record | Shows success/error |
| Handover SPD | Click | Valid ID | Status becomes SPD | |
| Handover Production | Click | Valid ID | Status becomes production | |
| Stakeholders Add | Submit | Name and Email required | Adds stakeholder | Inline row form |
| Stakeholders Edit | Submit | ID valid | Updates name/email | Two-column manage section |
| Stakeholders Delete | Click | Confirm checked | Deletes stakeholder | Requires confirmation |
| Reports | View | N/A | Shows critical (<10.5V) table | |
| Send Email Report | Click | Disabled if no stakeholders | Simulated success | SMTP not configured |

## Status Logic

- Voltage status color helper (used for metrics and potential styling):
  - `<10.5V` red
  - `10.5-11V` yellow
  - `>=11V` green

## Notes

- All CRUD operations are performed via pandas on Excel files.
- `utils/` contains modularized logic for batteries and stakeholders.
- The app ensures Excel files are present and initialized on first use.


