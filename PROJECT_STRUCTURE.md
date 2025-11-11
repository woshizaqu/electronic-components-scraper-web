# 项目结构说明

## 目录结构

```
电子元器件爬虫v0/
├── main.py                 # 程序入口文件
├── gui_app.py              # 图形用户界面实现
├── mouser_api.py           # Mouser API接口封装
├── excel_handler.py        # Excel文件处理模块
├── config.py               # 配置文件
├── requirements.txt        # 依赖包列表
├── README.md               # 项目说明文档
├── PROJECT_STRUCTURE.md    # 项目结构说明
├── 元件列表.txt            # 示例元件列表文件
├── 贸泽电子元件查询模板.xlsx  # Excel输入模板
├── __pycache__/            # Python缓存目录
└── .venv/                  # 虚拟环境目录
```

## 文件详细说明

### 1. main.py
程序的入口文件，负责启动GUI应用程序。

### 2. gui_app.py
图形用户界面的实现文件，使用CustomTkinter库构建：
- 支持单个元件输入
- 支持批量元件输入（文本框）
- 支持文件导入（Excel和TXT格式）
- 实时显示搜索进度和结果
- 支持结果导出到Excel

### 3. mouser_api.py
Mouser API接口封装模块：
- 实现API密钥轮换机制
- 封装搜索元件和相似元件的功能
- 提取价格信息（最大批次对应的价格）
- 处理API速率限制

### 4. excel_handler.py
Excel文件处理模块：
- 创建输入模板
- 读取元件列表（Excel和TXT格式）
- 导出查询结果

### 5. config.py
配置文件，包含：
- Mouser API密钥列表
- API请求限制配置
- 文件名配置
- API端点配置

### 6. requirements.txt
项目依赖包列表：
- requests: HTTP请求库
- openpyxl: Excel文件处理
- pandas: 数据处理
- customtkinter: 现代化GUI库

### 7. 元件列表.txt
示例元件列表文件，包含50个常用电子元件型号。

### 8. 贸泽电子元件查询模板.xlsx
Excel输入模板，用户可按照此模板格式填写元件信息。

## 功能特性

### 用户界面
- 美观的现代化GUI界面
- 支持多种输入方式
- 实时进度显示
- 结果实时展示

### API处理
- 多API密钥轮换使用
- 速率限制控制
- 错误处理机制
- 相似型号搜索

### 文件处理
- Excel模板生成和读取
- TXT文件读取
- 结果导出到Excel
- 自动列宽调整

### 批量处理
- 支持大量元件查询（最多14万个）
- 进度跟踪
- 结果汇总

## 使用流程

1. 运行`main.py`启动程序
2. 通过以下方式输入元件型号：
   - 单个输入框输入
   - 批量文本框输入（每行一个）
   - 导入Excel或TXT文件
3. 点击"搜索价格"开始查询
4. 查看实时结果
5. 导出结果到Excel文件

## 配置说明

在`config.py`中可以调整以下参数：

- `MOUSER_API_KEYS`: Mouser API密钥列表（已配置三个）
- `MAX_REQUESTS_PER_MINUTE`: 每分钟最大请求数
- `REQUEST_DELAY`: 请求间隔时间（秒）
- `OUTPUT_EXCEL_TEMPLATE`: 输入模板文件名
- `OUTPUT_EXCEL_RESULT`: 结果文件名
- `INPUT_TXT_FILE`: 示例TXT文件名