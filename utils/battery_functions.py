from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from .excel_handler import (
	DATA_DIR,
	append_row,
	ensure_file,
	generate_next_id,
	read_excel,
	write_excel,
)


BATTERIES_XLSX = DATA_DIR / "batteries.xlsx"
STAKEHOLDERS_XLSX = DATA_DIR / "stakeholders.xlsx"
CHECKS_XLSX = DATA_DIR / "battery_checks.xlsx"


def ensure_all_files() -> None:
	ensure_file(BATTERIES_XLSX, [
		"id",
		"product_number",
		"current_voltage",
		"last_checked_date",
		"packing_month",
		"status",
		"total_checks",
	])
	ensure_file(STAKEHOLDERS_XLSX, ["id", "name", "email"])
	ensure_file(CHECKS_XLSX, [
		"id",
		"battery_id",
		"voltage_reading",
		"voltage_during_check",
		"checked_by",
		"notes",
		"checked_at",
	])


def read_batteries() -> pd.DataFrame:
	ensure_all_files()
	return read_excel(BATTERIES_XLSX)


def save_batteries(df: pd.DataFrame) -> None:
	write_excel(df, BATTERIES_XLSX)


def scan_battery(identifier: str) -> Optional[pd.Series]:
	"""Find a battery by id or product_number."""
	df = read_batteries()
	if df.empty:
		return None
	# Try id exact match
	try:
		ident_int = int(identifier)
		match = df.loc[df["id"] == ident_int]
		if not match.empty:
			return match.iloc[0]
	except Exception:
		pass
	# Try product number exact match (string compare)
	match = df.loc[df["product_number"].astype(str).str.strip() == str(identifier).strip()]
	if not match.empty:
		return match.iloc[0]
	return None


def add_battery(product_number: str, packing_month: str | None = None, initial_voltage: float | None = None) -> pd.Series:
	df = read_batteries()
	new_id = generate_next_id(df)
	row = {
		"id": new_id,
		"product_number": product_number,
		"current_voltage": initial_voltage if initial_voltage is not None else None,
		"last_checked_date": None,
		"packing_month": packing_month,
		"status": "active",
		"total_checks": 0,
	}
	df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
	save_batteries(df)
	return df.loc[df["id"] == new_id].iloc[0]


def delete_battery(battery_id: int) -> bool:
	df = read_batteries()
	before = len(df)
	df = df.loc[df["id"] != battery_id]
	save_batteries(df)
	return len(df) < before


def update_voltage(
	battery_id: int,
	voltage_reading: float,
	checked_by: str,
	notes: str | None = None,
	voltage_during_check: float | None = None,
) -> pd.Series:
	"""Update a battery's voltage, increment total_checks, create a check row."""
	ensure_all_files()
	b_df = read_batteries()
	if b_df.empty or battery_id not in set(b_df["id"]):
		raise ValueError("Battery not found")
	row_idx = b_df.index[b_df["id"] == battery_id][0]
	b_df.at[row_idx, "current_voltage"] = voltage_reading
	b_df.at[row_idx, "last_checked_date"] = datetime.now()
	b_df.at[row_idx, "total_checks"] = int(b_df.at[row_idx, "total_checks"] or 0) + 1
	save_batteries(b_df)

	checks_df = read_excel(CHECKS_XLSX)
	new_check_id = generate_next_id(checks_df)
	check_row = {
		"id": new_check_id,
		"battery_id": battery_id,
		"voltage_reading": voltage_reading,
		"voltage_during_check": voltage_during_check,
		"checked_by": checked_by,
		"notes": notes,
		"checked_at": datetime.now(),
	}
	append_row(CHECKS_XLSX, check_row)
	return b_df.loc[b_df["id"] == battery_id].iloc[0]


def handover_status(battery_id: int, new_status: str) -> pd.Series:
	b_df = read_batteries()
	if b_df.empty or battery_id not in set(b_df["id"]):
		raise ValueError("Battery not found")
	row_idx = b_df.index[b_df["id"] == battery_id][0]
	b_df.at[row_idx, "status"] = new_status
	save_batteries(b_df)
	return b_df.loc[b_df["id"] == battery_id].iloc[0]


def filter_inventory(
	product_query: Optional[str] = None,
	status: Optional[str] = None,
	voltage_min: Optional[float] = None,
	voltage_max: Optional[float] = None,
) -> pd.DataFrame:
	df = read_batteries()
	if product_query:
		df = df[df["product_number"].astype(str).str.contains(str(product_query), case=False, na=False)]
	if status:
		df = df[df["status"].astype(str) == status]
	if voltage_min is not None:
		df = df[pd.to_numeric(df["current_voltage"], errors="coerce") >= float(voltage_min)]
	if voltage_max is not None:
		df = df[pd.to_numeric(df["current_voltage"], errors="coerce") <= float(voltage_max)]
	return df


def status_color(voltage: Optional[float]) -> str:
	"""Determine color status based on voltage."""
	if voltage is None:
		return "gray"
	if voltage < 10.5:
		return "red"
	if voltage < 11.0:
		return "yellow"
	return "green"


