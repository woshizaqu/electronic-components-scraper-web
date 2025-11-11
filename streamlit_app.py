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