import pandas as pd
from pathlib import Path
from typing import Optional


# Resolve data directory relative to this file to avoid CWD issues when running Streamlit
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def ensure_file(file_path: str | Path, columns: list[str]) -> Path:
	"""Ensure an Excel file exists with the provided columns."""
	path = Path(file_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	if not path.exists():
		pd.DataFrame(columns=columns).to_excel(path, index=False)
	return path


def read_excel(file_path: str | Path) -> pd.DataFrame:
	return pd.read_excel(file_path)


def write_excel(df: pd.DataFrame, file_path: str | Path) -> None:
	df.to_excel(file_path, index=False)


def append_row(file_path: str | Path, row: dict) -> pd.DataFrame:
	"""Append a single row to an Excel sheet and return the updated DataFrame."""
	df = read_excel(file_path)
	df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
	write_excel(df, file_path)
	return df


def generate_next_id(df: pd.DataFrame, id_column: str = "id") -> int:
	if df.empty:
		return 1
	return int(df[id_column].max()) + 1


