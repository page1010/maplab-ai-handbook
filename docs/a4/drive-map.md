# A4 Drive Map

## Verified source

```text
 photos/Takeout/Google 相簿 (1jNUnnXPYMEq3GLDiJNC1GFZjQWRvwcCz)
└── Google 相簿 (18Y1vXHrlzp8Ot3TV2-qN02YPi3hBhgdk)
    ├── 2021 年的相片
    ├── 2022 年的相片
    ├── 2023 年的相片
    ├── 2024 年的相片
    ├── 2025 年的相片
    ├── 2026 年的相片
    ├── 垃圾桶
    └── 失敗的影片
```

## Verified MAPLAB workspace root

```text
MAPLAB (1SLIMAtjN6XSCYUTXRPe2XrkAO7sT-B0l)
├── MAPLAB_ASSET_LOG
├── MAPLAB_ASSETS (1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy)
└── photos
```

Read-only API verification on 2026-05-11 confirmed `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy` is the current `MAPLAB_ASSETS` folder under `MAPLAB`.

## Destination tree references

Repo history mentions the following `MAPLAB_ASSETS` roots:

- `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe`
- `1yVggYKiTkBJe4kd8CPoM3U75kmOnVuNy`
- `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy`

Treat `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy` as the verified destination root in the current connector session.
Treat `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe` as invalid for current operations: Drive API returned 404 on 2026-05-11.

## Folder split policy

When the active destination root is confirmed, split by purpose first:

- `catering/`
- `travel/`
- `daily/`

Then split by year where needed:

- `2022/`
- `2023/`
- `2024/`
- `2025/`
- `2026/`

## Notes

- Source and destination must not be mixed.
- The workbook should record what was planned, copied, skipped, or missing.
