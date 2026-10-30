# YouTube Data Engineering Pipeline

Dự án ETL thu thập dữ liệu video từ **YouTube Data API v3**, chuẩn hóa bằng Python và lưu vào **Google BigQuery**. Pipeline hỗ trợ nạp video chưa có trong kho dữ liệu, cập nhật thống kê và lưu lịch sử theo từng lần chạy.

## Luồng dữ liệu

```text
YouTube uploads playlist
        │
        ▼
Đọc danh sách video ── Đối chiếu video_id trong BigQuery
        │
        ▼
Lấy chi tiết video mới → Chuẩn hóa → data/clean/incremental.ndjson
        │
        ▼
youtube_raw.staging_videos → MERGE → youtube_clean.videos
        │
        ▼
youtube_raw.pipeline_checkpoints

Video đã có trong BigQuery → Lấy thống kê mới
        │
        ▼
youtube_raw.staging_video_stats
        ├── MERGE → youtube_clean.video_stats_history
        └── UPDATE → youtube_clean.videos
```

- **Nạp tăng dần:** so sánh toàn bộ danh sách video của playlist với `video_id` đã lưu theo kênh, chỉ lấy chi tiết cho video mới.
- **Chuẩn hóa:** chuyển thời lượng ISO 8601 thành giây, chuyển số lượt xem/thích/bình luận thành số nguyên và bổ sung thời điểm trích xuất UTC.
- **Lưu checkpoint:** ghi trạng thái thành công và video đầu playlist sau khi xử lý; việc tìm video mới hiện dựa trên bảng `videos`, không dựa vào checkpoint.
- **Lịch sử thống kê:** lưu snapshot theo `video_id`, `run_id`, `snapshot_date` và cập nhật các chỉ số mới nhất trong bảng `videos`.
- **Retry API:** thử lại tối đa 5 lần với HTTP `429`, `500`, `502`, `503`, `504`, có thời gian chờ tăng dần.

## Cấu trúc dự án

```text
.
├── config/setting.py              # Đọc cấu hình từ môi trường và .env
├── etl/
│   ├── extract/                   # Đọc playlist, chi tiết và thống kê video
│   ├── transform/video.py         # Chuẩn hóa bản ghi video
│   ├── load/                      # Nạp staging và MERGE vào BigQuery
│   └── utils/                     # Checkpoint, retry, lưu JSON raw
├── data/
│   ├── artists.csv                # Dữ liệu nghệ sĩ mẫu
│   ├── raw/                       # JSON nguồn cục bộ, được Git bỏ qua
│   └── clean/                     # JSON/NDJSON đã chuẩn hóa
├── incremental_pipeline.py        # Pipeline nạp video mới
├── stats_refresh_pipeline.py      # Cập nhật thống kê và lưu lịch sử
├── transform_main.py              # Chuẩn hóa JSON raw cục bộ
├── prepare_bigquery.py            # Chuyển clean JSON thành NDJSON
├── main.py                        # Script trích xuất ban đầu; xem lưu ý bên dưới
├── load_main.py                   # Script nạp staging với dữ liệu mẫu cố định
├── incremental_main.py            # Script kiểm tra đối chiếu ID
├── test/                          # Unit test và script kiểm tra dữ liệu
├── .env.example
└── requirements.txt
```

## Cài đặt

Cần Python, môi trường ảo, API key cho YouTube Data API v3 và một Google Cloud project có BigQuery. Cache trong dự án được tạo bằng Python 3.14; repository chưa khai báo phiên bản Python tối thiểu.

```bash
git clone https://github.com/khoacao83/Big_project1.git
cd Big_project1
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Trên Windows PowerShell, kích hoạt môi trường bằng `.venv\Scripts\Activate.ps1` và sao chép cấu hình bằng `Copy-Item .env.example .env`.

### Cấu hình môi trường

Điền các biến sau vào `.env` tại thư mục gốc dự án:

```dotenv
YOUTUBE_API_KEY=your_youtube_api_key
GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id
BQ_LOCATION=asia-southeast1
CHANNEL_ID=UC_x5XG1OV2P6uZZ5FSM9Ttw
UPLOADS_PLAYLIST_ID=UU_x5XG1OV2P6uZZ5FSM9Ttw
```

| Biến | Ý nghĩa | Giá trị mặc định trong mã |
| --- | --- | --- |
| `YOUTUBE_API_KEY` | API key để gọi YouTube | Bắt buộc |
| `GOOGLE_CLOUD_PROJECT` | Project chứa các bảng BigQuery | `youtube-de-project1` |
| `BQ_LOCATION` | Vùng dùng bởi module merge và checkpoint | `asia-southeast1` |
| `CHANNEL_ID` | ID kênh cần thu thập, bắt đầu bằng `UC` | Kênh mẫu như trên |
| `UPLOADS_PLAYLIST_ID` | Uploads playlist tương ứng của kênh | Playlist mẫu như trên |

Cấu hình còn đọc `TEST_CHANNEL_ID` và `TEST_UPLOADS_PLAYLIST_ID` nếu chưa đặt hai biến tương ứng. Các bước load và cập nhật thống kê hiện gắn cứng vùng `asia-southeast1`, vì vậy hãy dùng vùng này cho cả hai dataset.

BigQuery dùng thông tin xác thực mặc định của Google Cloud (ADC), tách biệt với API key YouTube. Nếu đã cài Google Cloud CLI, có thể đăng nhập cục bộ bằng:

```bash
gcloud auth application-default login
```

Tài khoản chạy cần quyền tạo job truy vấn và đọc/ghi các bảng của dự án. Giữ `.env` và file khóa tài khoản dịch vụ ngoài Git.

## Chuẩn bị BigQuery

Repository chưa có migration tự tạo dataset/bảng. Trước lần chạy đầu tiên, chạy SQL dưới đây trong BigQuery, thay **mọi** `YOUR_PROJECT_ID` bằng project đã cấu hình. Schema này bám theo các trường được mã Python và câu lệnh MERGE sử dụng.

```sql
CREATE SCHEMA IF NOT EXISTS `YOUR_PROJECT_ID.youtube_raw`
OPTIONS(location = 'asia-southeast1');

CREATE SCHEMA IF NOT EXISTS `YOUR_PROJECT_ID.youtube_clean`
OPTIONS(location = 'asia-southeast1');

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.youtube_raw.staging_videos` (
  artist_name STRING,
  channel_id STRING,
  channel_title STRING,
  video_id STRING,
  video_title STRING,
  description STRING,
  published_at TIMESTAMP,
  duration_seconds INT64,
  tags ARRAY<STRING>,
  category_id STRING,
  view_count INT64,
  like_count INT64,
  comment_count INT64,
  extracted_at TIMESTAMP,
  source STRING,
  ingestion_date DATE
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.youtube_clean.videos`
LIKE `YOUR_PROJECT_ID.youtube_raw.staging_videos`;

ALTER TABLE `YOUR_PROJECT_ID.youtube_clean.videos`
ADD COLUMN IF NOT EXISTS stats_updated_at TIMESTAMP;

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.youtube_raw.pipeline_checkpoints` (
  channel_id STRING,
  uploads_playlist_id STRING,
  last_seen_video_id STRING,
  status STRING,
  last_success_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.youtube_raw.staging_video_stats` (
  video_id STRING,
  channel_id STRING,
  view_count INT64,
  like_count INT64,
  comment_count INT64,
  snapshot_at TIMESTAMP,
  snapshot_date DATE,
  run_id STRING
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.youtube_clean.video_stats_history` (
  video_id STRING,
  channel_id STRING,
  view_count INT64,
  like_count INT64,
  comment_count INT64,
  snapshot_at TIMESTAMP,
  snapshot_date DATE,
  run_id STRING
)
PARTITION BY snapshot_date
CLUSTER BY channel_id, video_id;
```

`CREATE TABLE IF NOT EXISTS` không bổ sung trường còn thiếu cho bảng đã tồn tại. Nếu đã có bảng từ phiên bản trước, cần đối chiếu và cập nhật schema trước khi chạy.

## Chạy pipeline

Chạy các lệnh từ thư mục gốc repository sau khi kích hoạt môi trường ảo.

### 1. Nạp video mới

```bash
python -m incremental_pipeline
```

Lần đầu, nếu bảng `videos` rỗng, pipeline lấy chi tiết tất cả video mà API trả về trong uploads playlist. Các lần sau chỉ lấy chi tiết video chưa có trong bảng. Khi không có video mới, pipeline ghi checkpoint rồi kết thúc.

Dữ liệu chuẩn hóa được ghi vào `data/clean/incremental.ndjson`, nạp vào `youtube_raw.staging_videos`, sau đó MERGE vào `youtube_clean.videos` theo `video_id`.

### 2. Cập nhật thống kê

```bash
# Mặc định xử lý 5 video, theo thứ tự video_id
python -m stats_refresh_pipeline

# Cập nhật toàn bộ video đã lưu của kênh
python -m stats_refresh_pipeline --limit 0

# Chỉ xử lý 100 video
python -m stats_refresh_pipeline --limit 100

# Gán run ID để dùng lại khi chạy lại cùng đợt
python -m stats_refresh_pipeline --limit 100 --run-id refresh-2026-10-31
```

`--limit` chọn các ID đầu tiên theo thứ tự `video_id`, không phải các video mới nhất hoặc một cơ chế luân phiên. Lịch sử dùng bộ khóa `video_id`, `run_id`, `snapshot_date`: dùng lại run ID trong cùng ngày UTC giúp tránh chèn lại các snapshot đã có; chạy sang ngày khác sẽ tạo snapshot mới.

### 3. Xử lý file cục bộ

Nếu đã có JSON raw hợp lệ chứa khóa `video` trong `data/raw/`:

```bash
python -m transform_main
python -m prepare_bigquery
python -m test.check_transform
```

Hai bước đầu chọn file cuối theo thứ tự tên: `*.json` trong thư mục raw, rồi `*_clean.json` trong thư mục clean. `prepare_bigquery.py` chỉ chuyển đổi sang NDJSON, không tạo bảng hay nạp lên BigQuery.

## Kiểm tra

Unit test cho việc tìm ID mới và đọc cấu hình:

```bash
python -m unittest test.test_incremental -v
```

Kiểm tra chất lượng dữ liệu cục bộ, cần có file đầu vào tương ứng:

```bash
python -m test.check_quality_video
python -m test.check_transform
```

Các kiểm tra này đối chiếu ID thiếu/trùng và các giá trị âm của lượt xem, thời lượng. Chúng không thay thế kiểm thử tích hợp YouTube/BigQuery.

## Lưu ý hiện tại

- `main.py` và một số script thử nghiệm cũ còn import `TEST_CHANNEL_ID`, trong khi `config/setting.py` hiện xuất `CHANNEL_ID`. Cần cập nhật mã trước khi dùng các script đó; đặt biến trong `.env` không tự sửa lỗi import. Luồng nạp chính là `incremental_pipeline.py`.
- `load_main.py` gắn cứng project, tên file NDJSON và số lượng kỳ vọng 6.120 bản ghi. Cần sửa các giá trị này nếu dùng dữ liệu khác; script chỉ nạp staging.
- Pipeline incremental không tự cập nhật video đã có hoặc xóa video không còn trong playlist. Dùng pipeline thống kê để làm mới lượt xem, lượt thích và bình luận.
- Các bảng staging được ghi đè bằng `WRITE_TRUNCATE`. Tránh chạy đồng thời nhiều tiến trình dùng chung một bảng staging.
- Dự án chưa tích hợp lịch chạy tự động. Các pipeline hiện được chạy bằng lệnh Python.
- `.env`, cache Python và `data/raw/` được Git bỏ qua; các file dữ liệu mẫu trong `data/clean/` hiện được lưu trong repository.

## Xử lý lỗi thường gặp

| Hiện tượng | Cách kiểm tra |
| --- | --- |
| `YOUTUBE_API_KEY is missing from .env` | Điền API key và chạy từ thư mục gốc dự án. |
| Không tìm thấy bảng/dataset | Tạo các bảng ở phần chuẩn bị BigQuery và kiểm tra project ID. |
| Lỗi xác thực BigQuery | Kiểm tra ADC và quyền đọc/ghi bảng, chạy job của tài khoản. |
| Lỗi vùng BigQuery | Kiểm tra cả hai dataset nằm ở `asia-southeast1`. |
| API trả về thiếu video | Pipeline chủ động dừng nếu thiếu chi tiết/thống kê; kiểm tra khả năng truy cập video rồi chạy lại. |
| HTTP `403` do quota | Kiểm tra quota/API key; mã retry hiện không tự thử lại lỗi `403`. |
| Không có raw JSON hoặc JSON không hợp lệ | Cung cấp file raw hợp lệ cho bước xử lý cục bộ, hoặc dùng pipeline incremental. |
