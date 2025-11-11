# Streamlit Community Cloud 部署与自定义域名配置手册

本手册将详细介绍如何将电子元器件爬虫工具部署到 Streamlit Community Cloud 并配置自定义域名。

## 目录

1. [Streamlit Community Cloud 简介](#streamlit-community-cloud-简介)
2. [准备工作](#准备工作)
3. [代码适配](#代码适配)
4. [部署到 Streamlit Community Cloud](#部署到-streamlit-community-cloud)
5. [配置自定义域名](#配置自定义域名)
6. [常见问题与解决方案](#常见问题与解决方案)

## Streamlit Community Cloud 简介

Streamlit Community Cloud 是 Streamlit 官方提供的免费云部署服务，具有以下特点：
- 免费部署 Python 应用
- 支持 GitHub 集成
- 自动 SSL 证书
- 可配置自定义域名
- 每月 1000 小时运行时间
- 支持私有和公开应用

## 准备工作

### 1. 注册 GitHub 账户
如果还没有 GitHub 账户，请先注册：
1. 访问 [GitHub](https://github.com/)
2. 点击 "Sign up"
3. 按照提示完成注册

### 2. 准备项目代码
确保您的项目代码已经推送到 GitHub 仓库。

### 3. 注册 Streamlit Community Cloud
1. 访问 [Streamlit Community Cloud](https://streamlit.io/cloud)
2. 点击 "Sign up"
3. 使用 GitHub 账户登录

## 代码适配

### 1. 安装 Streamlit
首先需要在项目中添加 Streamlit 依赖：
```bash
pip install streamlit
```

更新 [requirements.txt](file:///e:/应用下载/Qoder/Qoder项目/电子元器件爬虫v0/requirements.txt) 文件：
```txt
streamlit==1.28.0
requests==2.31.0
openpyxl==3.1.2
pandas==2.0.3
```

### 2. 创建 Streamlit 应用
创建 [streamlit_app.py](file:///e:/应用下载/Qoder/Qoder项目/电子元器件爬虫v0/streamlit_app.py) 文件：

```python
import streamlit as st
import pandas as pd
from io import BytesIO
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mouser_api import MouserAPI
from excel_handler import ExcelHandler

# 页面配置
st.set_page_config(
    page_title="贸泽电子元器件价格爬虫",
    page_icon="🔍",
    layout="wide"
)

# 初始化处理器
excel_handler = ExcelHandler()

# 页面标题
st.title("🔍 贸泽电子元器件价格爬虫")

# 侧边栏
st.sidebar.header("设置")

# API密钥输入
api_key = st.sidebar.text_input("Mouser API密钥", type="password")
st.sidebar.markdown("[获取API密钥](https://www.mouser.com/api-hub/)")

# 使用说明
st.sidebar.markdown("---")
st.sidebar.markdown("### 使用说明")
st.sidebar.markdown("""
1. 输入您的Mouser API密钥
2. 选择输入方式：
   - 单个元件查询
   - 批量元件查询
   - 文件上传
3. 点击搜索按钮
4. 查看和导出结果
""")

# 主界面
tab1, tab2, tab3 = st.tabs(["单个查询", "批量查询", "文件上传"])

# 单个元件查询
with tab1:
    st.header("单个元件查询")
    single_component = st.text_input("输入元件型号", placeholder="例如: LM358DR")
    
# 批量元件查询
with tab2:
    st.header("批量元件查询")
    batch_components = st.text_area("每行输入一个元件型号", height=200, placeholder="例如:\nLM358DR\nESP32-WROOM-32D\nTL072CDR")

# 文件上传
with tab3:
    st.header("文件上传")
    uploaded_file = st.file_uploader("上传Excel或TXT文件", type=["xlsx", "txt"])
    
    # 下载模板按钮
    if st.button("下载Excel模板"):
        try:
            # 创建Excel模板在内存中
            output = BytesIO()
            excel_handler.create_input_template(output)
            output.seek(0)
            
            st.download_button(
                label="点击下载模板",
                data=output,
                file_name="贸泽电子元件查询模板.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"下载模板时发生错误: {str(e)}")

# 搜索按钮
if st.button("🔍 搜索价格", type="primary"):
    if not api_key:
        st.error("请提供Mouser API密钥")
    else:
        # 初始化API
        mouser_api = MouserAPI()
        # 覆盖API密钥
        mouser_api.api_keys = [api_key]
        
        # 收集所有要搜索的元件型号
        components = []
        
        # 添加单个输入的元件
        if single_component:
            components.append(single_component)
        
        # 添加批量输入的元件
        if batch_components:
            batch_list = [line.strip() for line in batch_components.split('\n') if line.strip()]
            components.extend(batch_list)
        
        # 添加文件中的元件
        if uploaded_file is not None:
            try:
                filename = uploaded_file.name
                if filename.endswith('.xlsx'):
                    # 保存临时文件
                    temp_path = f"temp_{filename}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_components = excel_handler.read_components_from_excel(temp_path)
                    os.remove(temp_path)  # 清理临时文件
                elif filename.endswith('.txt'):
                    # 保存临时文件
                    temp_path = f"temp_{filename}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_components = excel_handler.read_components_from_txt(temp_path)
                    os.remove(temp_path)  # 清理临时文件
                else:
                    st.error("不支持的文件格式，请使用.xlsx或.txt文件")
                    st.stop()
                components.extend(file_components)
            except Exception as e:
                st.error(f"读取文件时发生错误: {str(e)}")
                st.stop()
        
        if not components:
            st.warning("请至少输入一个元件型号")
        else:
            # 显示进度
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 搜索元件
            results = []
            total_components = len(components)
            
            for i, component in enumerate(components):
                try:
                    # 更新进度
                    progress = (i + 1) / total_components
                    progress_bar.progress(progress)
                    status_text.text(f"正在搜索: {component} ({i+1}/{total_components})")
                    
                    # 搜索元件
                    part_data = mouser_api.search_part(component)
                    
                    if part_data:
                        # 提取价格信息
                        price, quantity = mouser_api.extract_pricing_info(part_data)
                        
                        # 检查是否停产
                        is_discontinued = mouser_api.is_discontinued(part_data)
                        
                        # 获取替代型号
                        replacement_part = mouser_api.get_replacement_part(part_data)
                        
                        # 设置备注信息
                        if is_discontinued and price == 0:
                            remark = "已停产无价格"
                        elif is_discontinued:
                            remark = "已停产"
                        elif price == 0:
                            remark = "无价格信息"
                        else:
                            remark = ""
                        
                        result = {
                            "元件型号": component,
                            "搜索型号": component,
                            "产品名称": part_data.get("ManufacturerPartNumber", ""),
                            "品牌": part_data.get("Manufacturer", ""),
                            "价格": price,
                            "最大批次": quantity,
                            "库存": part_data.get("Availability", ""),
                            "是否停产": "是" if is_discontinued else "否",
                            "替代型号": replacement_part,
                            "备注": remark
                        }
                    else:
                        # 尝试搜索相似型号
                        similar_part_data = mouser_api.search_similar_part(component)
                        if similar_part_data:
                            # 提取价格信息
                            price, quantity = mouser_api.extract_pricing_info(similar_part_data)
                            
                            # 检查是否停产
                            is_discontinued = mouser_api.is_discontinued(similar_part_data)
                            
                            # 获取替代型号
                            replacement_part = mouser_api.get_replacement_part(similar_part_data)
                            
                            # 设置备注信息
                            if is_discontinued and price == 0:
                                remark = "已停产无价格"
                            elif is_discontinued:
                                remark = "已停产"
                            elif price == 0:
                                remark = "无价格信息"
                            else:
                                remark = "相似型号爬取"
                            
                            result = {
                                "元件型号": component,
                                "搜索型号": similar_part_data.get("ManufacturerPartNumber", ""),
                                "产品名称": similar_part_data.get("ManufacturerPartNumber", ""),
                                "品牌": similar_part_data.get("Manufacturer", ""),
                                "价格": price,
                                "最大批次": quantity,
                                "库存": similar_part_data.get("Availability", ""),
                                "是否停产": "是" if is_discontinued else "否",
                                "替代型号": replacement_part,
                                "备注": remark
                            }
                        else:
                            result = {
                                "元件型号": component,
                                "搜索型号": "",
                                "产品名称": "",
                                "品牌": "",
                                "价格": 0,
                                "最大批次": 0,
                                "库存": "",
                                "是否停产": "否",
                                "替代型号": "",
                                "备注": "未找到"
                            }
                    
                    results.append(result)
                    
                except Exception as e:
                    error_result = {
                        "元件型号": component,
                        "搜索型号": "",
                        "产品名称": "",
                        "品牌": "",
                        "价格": 0,
                        "最大批次": 0,
                        "库存": "",
                        "是否停产": "否",
                        "替代型号": "",
                        "备注": f"错误: {str(e)}"
                    }
                    results.append(error_result)
            
            progress_bar.empty()
            status_text.empty()
            st.success(f"搜索完成，共处理 {total_components} 个元件")
            
            # 显示结果
            if results:
                df = pd.DataFrame(results)
                
                # 显示结果表格
                st.subheader("查询结果")
                st.dataframe(df, use_container_width=True)
                
                # 导出结果
                st.subheader("导出结果")
                
                # 创建Excel文件在内存中
                output = BytesIO()
                excel_handler.create_result_template(results, output)
                output.seek(0)
                
                st.download_button(
                    label="📥 导出为Excel",
                    data=output,
                    file_name="贸泽电子元件价格查询结果.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("没有找到任何结果")

# 页脚
st.markdown("---")
st.markdown("© 2025 贸泽电子元器件价格爬虫工具")
```

### 3. 更新配置文件
修改 [config.py](file:///e:/应用下载/Qoder/Qoder项目/电子元器件爬虫v0/config.py) 文件，添加Streamlit兼容性配置：

```python
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
```

## 部署到 Streamlit Community Cloud

### 1. 推送代码到 GitHub
确保您的代码已经推送到 GitHub 仓库：
```bash
git add .
git commit -m "Add Streamlit support"
git push origin main
```

### 2. 在 Streamlit Community Cloud 上部署
1. 登录 [Streamlit Community Cloud](https://share.streamlit.io/)
2. 点击 "New app"
3. 选择您的 GitHub 仓库
4. 配置以下设置：
   - Repository: 选择您的仓库
   - Branch: main (或您的主分支)
   - Main file path: streamlit_app.py
5. 点击 "Deploy!"

### 3. 等待部署完成
部署过程可能需要几分钟时间。部署完成后，您将获得一个类似 `your-app-name.streamlit.app` 的URL。

## 配置自定义域名

### 1. 购买域名
如果您还没有域名，需要先购买一个：
1. 访问域名注册商（如阿里云、腾讯云、Godaddy等）
2. 搜索并购买您喜欢的域名

### 2. 在域名提供商处配置DNS记录
您需要添加一个CNAME记录指向您的Streamlit应用：

1. 登录您的域名管理控制台
2. 找到DNS管理或域名解析设置
3. 添加一个新的CNAME记录：
   - 名称/主机记录: `your-subdomain` (例如: `components`)
   - 类型: CNAME
   - 值/记录值: `your-app-name.streamlit.app`
   - TTL: 600 或默认值

例如：
```
主机记录: components
记录类型: CNAME
记录值: your-app-name.streamlit.app
TTL: 600
```

### 3. 在 Streamlit Community Cloud 上配置自定义域名
1. 在 Streamlit Community Cloud 控制台找到您的应用
2. 点击 "Edit app settings"
3. 在 "Custom subdomain" 字段中输入您的子域名（例如: `components`）
4. 在 "Custom domain" 字段中输入您的完整域名（例如: `components.yourdomain.com`）
5. 点击 "Save"

### 4. 等待SSL证书配置
Streamlit会自动为您的自定义域名配置SSL证书，这可能需要几分钟到几小时时间。

## 常见问题与解决方案

### 1. 部署失败
**问题**: 应用部署失败
**解决方案**:
- 检查 [requirements.txt](file:///e:/应用下载/Qoder/Qoder项目/电子元器件爬虫v0/requirements.txt) 文件中的依赖是否正确
- 确保 [streamlit_app.py](file:///e:/应用下载/Qoder/Qoder项目/电子元器件爬虫v0/streamlit_app.py) 文件没有语法错误
- 查看部署日志获取详细错误信息

### 2. 自定义域名无法访问
**问题**: 配置自定义域名后无法访问
**解决方案**:
- 检查DNS记录是否正确配置
- 等待DNS传播（可能需要几分钟到几小时）
- 确认在Streamlit控制台正确配置了自定义域名

### 3. API请求失败
**问题**: 查询元件时返回错误
**解决方案**:
- 检查API密钥是否正确
- 确认API密钥在Mouser官网有效
- 检查网络连接是否正常

### 4. 文件上传失败
**问题**: 上传文件时出现错误
**解决方案**:
- 检查文件格式是否为.xlsx或.txt
- 确认文件大小不超过限制
- 验证文件内容格式是否正确

### 5. 应用运行缓慢
**问题**: 应用响应速度慢
**解决方案**:
- Streamlit Community Cloud的免费版本可能有性能限制
- 考虑减少单次查询的元件数量
- 优化代码逻辑，减少不必要的API调用

## 最佳实践建议

1. **API密钥安全**: 不要在代码中硬编码API密钥，建议用户在界面中手动输入
2. **错误处理**: 添加完善的错误处理机制，提供友好的错误提示
3. **性能优化**: 实现缓存机制，避免重复查询相同元件
4. **用户体验**: 提供清晰的使用说明和操作指引
5. **响应式设计**: 确保应用在不同设备上都能良好显示

## 参考资源

- [Streamlit官方文档](https://docs.streamlit.io/)
- [Streamlit Community Cloud文档](https://docs.streamlit.io/streamlit-cloud)
- [Mouser API文档](https://www.mouser.com/api-hub/)