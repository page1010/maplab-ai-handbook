#!/usr/bin/env zsh
set -euo pipefail

SRC_DIR="${ICCTN_SRC_DIR:-}"
OUT_DIR="workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001"
TMP_DIR="/private/tmp/icctn_heic_ql"
MANIFEST="$OUT_DIR/asset_conversion_manifest_icctn_001.csv"

if [[ -z "$SRC_DIR" ]]; then
  echo "ICCTN_SRC_DIR is required and must point to the synced Drive source folder." >&2
  exit 1
fi

mkdir -p "$OUT_DIR" "$TMP_DIR"

if ! command -v cwebp >/dev/null 2>&1; then
  echo "cwebp is required. Install with: brew install webp" >&2
  exit 1
fi

csv_escape() {
  local value="${1:-}"
  value="${value//\"/\"\"}"
  printf '"%s"' "$value"
}

file_size_bytes() {
  stat -f %z "$1"
}

image_width() {
  sips -g pixelWidth "$1" 2>/dev/null | awk '/pixelWidth:/ {print $2}'
}

image_height() {
  sips -g pixelHeight "$1" 2>/dev/null | awk '/pixelHeight:/ {print $2}'
}

printf 'source_file,source_format,source_bytes,output_file,output_bytes,width,height,alt_text,caption,usage_note\n' > "$MANIFEST"

records=(
  'IMG_20260612_145700.jpg|maplab-icc-tainan-catering-table-overview-01.webp|MAPLAB Kitchen 大臺南會展中心企業會議茶點外燴桌全景，含手指食物、甜點與飲品配置|大臺南會展中心企業會議茶點｜MAPLAB Kitchen 精緻外燴桌面配置|hero wide table'
  'IMG_20260612_145705.jpg|maplab-icc-tainan-catering-table-overview-02.webp|MAPLAB Kitchen 大臺南會展中心活動茶點桌，展示甜點、鹹點與會議接待餐點|大臺南會展中心活動茶點與手指食物配置|section wide table'
  'IMG_20260612_145735.jpg|maplab-icc-tainan-corporate-tea-table-03.webp|MAPLAB Kitchen 台南會展中心企業茶會點心桌，適合研討會與工作會議休息時段|台南會展中心企業茶會點心桌配置|case section'
  'IMG_20260612_145739.jpg|maplab-icc-tainan-finger-food-dessert-display-04.webp|MAPLAB Kitchen 大臺南會展中心手指食物與甜點外燴陳列，方便來賓取用與交流|大臺南會展中心手指食物與甜點陳列|detail'
  'IMG_20260612_145744.jpg|maplab-icc-tainan-dessert-catering-detail-05.webp|MAPLAB Kitchen 台南企業活動甜點外燴細節，適合會議茶點與品牌接待|台南企業活動甜點外燴細節|detail'
  'IMG_20260612_145746.jpg|maplab-icc-tainan-refreshment-dessert-table-06.webp|MAPLAB Kitchen 大臺南會展中心茶點擺設，包含甜點、鹹點與桌面層次配置|大臺南會展中心茶點擺設與桌面層次|detail'
  'IMG_20260612_145754.jpg|maplab-icc-tainan-catering-closeup-07.webp|MAPLAB Kitchen 台南會展外燴餐點近景，呈現企業活動茶點與小份量餐點|台南會展外燴餐點近景|detail'
  'IMG_20260612_145909.jpg|maplab-icc-tainan-event-refreshment-table-08.webp|MAPLAB Kitchen 大臺南會展中心活動茶點外燴桌，適合企業會議與貴賓接待|大臺南會展中心活動茶點外燴桌|section'
  'IMG_20260612_145919.jpg|maplab-icc-tainan-vip-reception-catering-09.webp|MAPLAB Kitchen 大臺南會展中心貴賓接待茶點，安排好拿取的手指食物與甜點|大臺南會展中心貴賓接待茶點|section'
  'IMG_20260612_145925.jpg|maplab-icc-tainan-meeting-refreshment-10.webp|MAPLAB Kitchen 大臺南會展中心會議茶點規劃，適合中場休息與交流時段|大臺南會展中心會議茶點規劃|section'
  'IMG_20260612_145930.jpg|maplab-icc-tainan-corporate-catering-display-11.webp|MAPLAB Kitchen 台南企業外燴桌面陳列，呈現會展中心活動餐點與接待質感|台南企業外燴桌面陳列|section'
  'IMG_1734.HEIC|maplab-icc-tainan-wide-refreshment-table-12.webp|MAPLAB Kitchen 大臺南會展中心企業會議茶點全景，展示外燴桌、飲品與點心配置|大臺南會展中心企業會議茶點全景|heic wide table'
  'IMG_1735.HEIC|maplab-icc-tainan-dessert-and-drink-service-13.webp|MAPLAB Kitchen 大臺南會展中心茶點與飲品服務區，適合企業活動接待與會議休息|大臺南會展中心茶點與飲品服務區|heic section'
  'IMG_1736.HEIC|maplab-icc-tainan-business-meeting-catering-14.webp|MAPLAB Kitchen 大臺南會展中心商務會議外燴，包含手指食物、甜點與接待餐桌|大臺南會展中心商務會議外燴餐桌|heic section'
)

for record in "${records[@]}"; do
  IFS='|' read -r source_name output_name alt_text caption usage_note <<< "$record"
  source_path="$SRC_DIR/$source_name"
  output_path="$OUT_DIR/$output_name"
  source_format="${source_name##*.}"
  source_format="${source_format:l}"
  conversion_input="$source_path"

  if [[ ! -f "$source_path" ]]; then
    echo "Missing source: $source_path" >&2
    exit 2
  fi

  if [[ "$source_format" == "heic" ]]; then
    qlmanage -t -s 1800 -o "$TMP_DIR" "$source_path" >/dev/null
    conversion_input="$TMP_DIR/$source_name.png"
    if [[ ! -f "$conversion_input" ]]; then
      echo "Quick Look did not produce thumbnail for $source_name" >&2
      exit 3
    fi
  fi

  cwebp -quiet -resize 1800 0 -q 78 -metadata none "$conversion_input" -o "$output_path"

  {
    csv_escape "$source_name"; printf ','
    csv_escape "$source_format"; printf ','
    printf '%s,' "$(file_size_bytes "$source_path")"
    csv_escape "$output_name"; printf ','
    printf '%s,' "$(file_size_bytes "$output_path")"
    printf '%s,' "$(image_width "$output_path")"
    printf '%s,' "$(image_height "$output_path")"
    csv_escape "$alt_text"; printf ','
    csv_escape "$caption"; printf ','
    csv_escape "$usage_note"; printf '\n'
  } >> "$MANIFEST"
done

echo "Wrote $MANIFEST"
