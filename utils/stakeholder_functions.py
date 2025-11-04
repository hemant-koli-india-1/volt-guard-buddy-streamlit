from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from .excel_handler import DATA_DIR, ensure_file, generate_next_id, read_excel, write_excel


STAKEHOLDERS_XLSX = DATA_DIR / "stakeholders.xlsx"


def ensure_stakeholders_file() -> None:
	ensure_file(STAKEHOLDERS_XLSX, ["id", "name", "email"])


def read_stakeholders() -> pd.DataFrame:
	ensure_stakeholders_file()
	return read_excel(STAKEHOLDERS_XLSX)


def save_stakeholders(df: pd.DataFrame) -> None:
	write_excel(df, STAKEHOLDERS_XLSX)


def add_stakeholder(name: str, email: str) -> pd.Series:
	df = read_stakeholders()
	new_id = generate_next_id(df)
	row = {"id": new_id, "name": name, "email": email}
	df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
	save_stakeholders(df)
	return df.loc[df["id"] == new_id].iloc[0]


def update_stakeholder(stakeholder_id: int, name: Optional[str] = None, email: Optional[str] = None) -> pd.Series:
	df = read_stakeholders()
	if df.empty or stakeholder_id not in set(df["id"]):
		raise ValueError("Stakeholder not found")
	row_idx = df.index[df["id"] == stakeholder_id][0]
	if name is not None:
		df.at[row_idx, "name"] = name
	if email is not None:
		df.at[row_idx, "email"] = email
	save_stakeholders(df)
	return df.loc[df["id"] == stakeholder_id].iloc[0]


def delete_stakeholder(stakeholder_id: int) -> bool:
	df = read_stakeholders()
	before = len(df)
	df = df.loc[df["id"] != stakeholder_id]
	save_stakeholders(df)
	return len(df) < before


