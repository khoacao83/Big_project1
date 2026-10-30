import json
from pathlib import Path

def main():
    files = sorted(
        Path("data/clean").glob("*_clean.json")
    )

    if not files:
        raise FileNotFoundError("No clean JSON found")

    input_path = files[-1]

    with input_path.open(encoding="utf-8") as f:
        records = json.load(f)

    output_path = input_path.with_suffix(".ndjson")

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    print("Total records:", len(records))
    print("NDJSON:", output_path)

if __name__ == "__main__":
    main()