from google.cloud import bigquery


def load_to_staging(project_id, ndjson_path):
    # 1. Initialize BigQuery client
    client = bigquery.Client(
        project=project_id,
        location="asia-southeast1"
    )

    # 2. Destination staging table
    table_id = (
        f"{project_id}.youtube_raw.staging_videos"
    )

    # 3. Configure load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=False,
        max_bad_records=0,
    )

    # 4. Load NDJSON file
    with open(ndjson_path, "rb") as file:
        job = client.load_table_from_file(
            file,
            table_id,
            job_config=job_config,
            location="asia-southeast1"
        )

    # 5. Wait until job finishes
    job.result()

    # 6. Print result
    print("Loaded rows:", job.output_rows)
    print("Job ID:", job.job_id)

    return job.output_rows