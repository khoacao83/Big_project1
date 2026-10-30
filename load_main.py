from pathlib import Path

from etl.load.bigquery import load_to_staging


PROJECT_ID = "youtube-de-project1"

NDJSON_PATH = Path(
    "data/clean/"
    "UC_x5XG1OV2P6uZZ5FSM9Ttw_"
    "20261027T084730Z_clean.ndjson"
)


def main():
    if not NDJSON_PATH.exists():
        raise FileNotFoundError(
            f"NDJSON file not found: {NDJSON_PATH}"
        )

    print("Starting BigQuery staging load...")

    loaded_rows = load_to_staging(
        project_id=PROJECT_ID,
        ndjson_path=str(NDJSON_PATH)
    )

    print(f"Total loaded rows: {loaded_rows}")

    if loaded_rows != 6120:
        raise RuntimeError(
            f"Expected 6120 rows, got {loaded_rows}"
        )

    print("Staging load completed successfully!")


if __name__ == "__main__":
    main()