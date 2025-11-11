import requests
import time
import config
from typing import Dict, List, Optional, Tuple

class MouserAPI:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys if api_keys is not None else config.MOUSER_API_KEYS
        self.current_key_index = 0
        self.request_count = 0
        self.last_request_time = 0
        
    def _get_next_api_key(self) -> str:
        """轮换到下一个API密钥"""
        api_key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return api_key
    
    def _rate_limit_check(self):
        """检查速率限制"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # 确保请求间隔
        if time_since_last_request < config.REQUEST_DELAY:
            time.sleep(config.REQUEST_DELAY - time_since_last_request)
            
        self.last_request_time = time.time()
    
    def search_part(self, part_number: str) -> Optional[Dict]:
        """
        搜索指定型号的电子元器件
        
        Args:
            part_number: 电子元器件型号
            
        Returns:
            包含产品信息的字典，如果未找到则返回None
        """
        self._rate_limit_check()
        
        # 获取当前API密钥
        api_key = self._get_next_api_key()
        
        # 构建请求URL
        url = f"{config.MOUSER_SEARCH_URL}?apiKey={api_key}"
        
        # 构建请求数据
        payload = {
            "SearchByPartRequest": {
                "mouserPartNumber": part_number,
                "partSearchOptions": "None"
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否找到了产品
                if "SearchResults" in data and data["SearchResults"]["NumberOfResult"] > 0:
                    return data["SearchResults"]["Parts"][0]  # 返回第一个匹配的产品
                
            elif response.status_code == 429:
                # 如果遇到速率限制，等待一段时间后重试
                time.sleep(5)
                return self.search_part(part_number)
                
        except Exception as e:
            print(f"搜索 {part_number} 时发生错误: {str(e)}")
            
        return None
    
    def search_similar_part(self, part_number: str) -> Optional[Dict]:
        """
        搜索相似型号的电子元器件
        
        Args:
            part_number: 电子元器件型号
            
        Returns:
            包含相似产品信息的字典，如果未找到则返回None
        """
        self._rate_limit_check()
        
        # 获取当前API密钥
        api_key = self._get_next_api_key()
        
        # 构建请求URL
        url = f"{config.MOUSER_SEARCH_URL}?apiKey={api_key}"
        
        # 构建请求数据，使用模糊搜索
        payload = {
            "SearchByPartRequest": {
                "mouserPartNumber": part_number,
                "partSearchOptions": "PartialMatch"
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否找到了产品
                if "SearchResults" in data and data["SearchResults"]["NumberOfResult"] > 0:
                    return data["SearchResults"]["Parts"][0]  # 返回第一个匹配的产品
                
            elif response.status_code == 429:
                # 如果遇到速率限制，等待一段时间后重试
                time.sleep(5)
                return self.search_similar_part(part_number)
                
        except Exception as e:
            print(f"搜索相似型号 {part_number} 时发生错误: {str(e)}")
            
        return None
    
    def extract_pricing_info(self, part_data: Dict) -> Tuple[float, int]:
        """
        提取产品的价格信息，返回最大批次的价格
        
        Args:
            part_data: 产品数据字典
            
        Returns:
            (价格, 批次数量) 元组
        """
        # 检查是否有价格信息
        if "PriceBreaks" not in part_data or not part_data["PriceBreaks"]:
            # 如果没有价格阶梯信息，尝试从其他字段获取
            if "Price" in part_data and part_data["Price"]:
                try:
                    # 尝试解析单价字段
                    price_str = part_data["Price"].replace("$", "").replace("¥", "").strip()
                    price = float(price_str)
                    # 尝试获取最小购买数量
                    min_qty = int(part_data.get("Min", "1")) if part_data.get("Min") else 1
                    return (price, min_qty)
                except (ValueError, TypeError):
                    pass
            return (0.0, 0)
        
        # 找到最大批次的数量和对应的价格
        max_quantity = 0
        price_for_max_quantity = 0.0
        
        for price_break in part_data["PriceBreaks"]:
            try:
                quantity = int(price_break["Quantity"])
                # 处理价格字符串，移除货币符号
                price_str = price_break["Price"].replace("$", "").replace("¥", "").replace("€", "").replace("£", "").strip()
                price = float(price_str)
                
                if quantity > max_quantity:
                    max_quantity = quantity
                    price_for_max_quantity = price
            except (ValueError, KeyError, TypeError):
                # 如果解析失败，跳过这个价格阶梯
                continue
                
        return (price_for_max_quantity, max_quantity)
    
    def is_discontinued(self, part_data: Dict) -> bool:
        """
        检查元件是否已停产
        
        Args:
            part_data: 产品数据字典
            
        Returns:
            如果元件已停产返回True，否则返回False
        """
        lifecycle_status = part_data.get("LifecycleStatus", "")
        return lifecycle_status == "Not Recommended for New Designs"
    
    def get_replacement_part(self, part_data: Dict) -> str:
        """
        获取推荐的替代型号
        
        Args:
            part_data: 产品数据字典
            
        Returns:
            推荐的替代型号，如果没有则返回空字符串
        """
        return part_data.get("SuggestedReplacement", "")