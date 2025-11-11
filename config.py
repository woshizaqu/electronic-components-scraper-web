# Mouser API 配置
MOUSER_API_KEYS = [
    "05956b6a-cac3-4d4d-b103-9aff3d2ea113",
    "629b2bc5-c07e-4da3-9d99-0ba1d6f9cb42",
    "6503fde5-25ba-40ee-a0d5-6a054d0aba65"
]

# API 请求限制配置
REQUEST_DELAY = 1  # 请求间隔(秒)

# 默认输出文件名
OUTPUT_EXCEL_TEMPLATE = "贸泽电子元件查询模板.xlsx"
OUTPUT_EXCEL_RESULT = "贸泽电子元件价格查询结果.xlsx"
INPUT_TXT_FILE = "元件列表.txt"

# API端点
MOUSER_SEARCH_URL = "https://api.mouser.com/api/v1/search/partnumber"