import random
import time

from googleapiclient.errors import HttpError

Retryable_status_codes={429, 500, 502, 503, 504}
# với các lỗi 403 quotaExceeded, 403 dailyLimitExceeded, 400 do request sai và 404 không nên retry liên tục. Các lỗi này cần xử lý riêng.
def execute_with_retry(request_history, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return request_history().execute()
        except HttpError as error:
            status = error.resp.status
            if status not in Retryable_status_codes:
                raise
            if attempt == max_attempts -1:
                raise
            delay = min(2 ** attempt, 30)
            delay += random.uniform(0,1)
            print(f"API error {status}" f"Retry after {delay:.1f}s")
            time.sleep(delay)            