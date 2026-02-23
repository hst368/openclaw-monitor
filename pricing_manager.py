"""
OpenClaw Monitor - Token Pricing Manager
管理模型定价配置，支持多货币、汇率转换
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List
import requests


class PricingManager:
    """Token 定价管理器"""
    
    CONFIG_DIR = os.path.expanduser('~/.openclaw-monitor')
    CONFIG_FILE = os.path.join(CONFIG_DIR, 'pricing.json')
    
    # 默认定价配置
    DEFAULT_PRICING = {
        "moonshot/kimi-k2.5": {
            "input_per_1k": 0.0005,
            "output_per_1k": 0.002,
            "currency": "CNY",
            "provider": "Moonshot"
        },
        "moonshot/kimi-k1.5": {
            "input_per_1k": 0.0002,
            "output_per_1k": 0.001,
            "currency": "CNY",
            "provider": "Moonshot"
        },
        "moonshot/kimi-k2": {
            "input_per_1k": 0.001,
            "output_per_1k": 0.004,
            "currency": "CNY",
            "provider": "Moonshot"
        },
        "gpt-4o": {
            "input_per_1k": 0.005,
            "output_per_1k": 0.015,
            "currency": "USD",
            "provider": "OpenAI"
        },
        "gpt-4o-mini": {
            "input_per_1k": 0.00015,
            "output_per_1k": 0.0006,
            "currency": "USD",
            "provider": "OpenAI"
        },
        "claude-3-opus": {
            "input_per_1k": 0.015,
            "output_per_1k": 0.075,
            "currency": "USD",
            "provider": "Anthropic"
        },
        "claude-3-sonnet": {
            "input_per_1k": 0.003,
            "output_per_1k": 0.015,
            "currency": "USD",
            "provider": "Anthropic"
        },
        "claude-3-haiku": {
            "input_per_1k": 0.00025,
            "output_per_1k": 0.00125,
            "currency": "USD",
            "provider": "Anthropic"
        },
        "deepseek-chat": {
            "input_per_1k": 0.00014,
            "output_per_1k": 0.00028,
            "currency": "CNY",
            "provider": "DeepSeek"
        },
        "default": {
            "input_per_1k": 0.003,
            "output_per_1k": 0.015,
            "currency": "USD",
            "provider": "Unknown"
        }
    }
    
    def __init__(self):
        os.makedirs(self.CONFIG_DIR, exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载定价配置"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载定价配置失败: {e}，使用默认配置")
        return self._create_default_config()
    
    def _create_default_config(self) -> dict:
        """创建默认配置"""
        config = {
            "currency": "CNY",
            "exchange_rate": {
                "USD_TO_CNY": 7.25,
                "CNY_TO_USD": 0.1379,
                "last_updated": datetime.now().isoformat(),
                "auto_update": True
            },
            "models": self.DEFAULT_PRICING.copy(),
            "history": []
        }
        self._save_config(config)
        return config
    
    def _save_config(self, config: dict):
        """保存配置到文件"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存定价配置失败: {e}")
    
    def get_model_pricing(self, model_name: str) -> dict:
        """获取模型定价"""
        models = self.config.get("models", {})
        
        # 精确匹配
        if model_name in models:
            return models[model_name]
        
        # 模糊匹配（如 "moonshot/kimi-k2.5" 匹配 "kimi-k2.5"）
        for key, value in models.items():
            if model_name in key or key in model_name:
                return value
        
        # 返回默认
        return models.get("default", self.DEFAULT_PRICING["default"])
    
    def update_model_pricing(self, model_name: str, 
                            input_price: float, 
                            output_price: float,
                            currency: str = None,
                            provider: str = "",
                            reason: str = "") -> bool:
        """更新模型定价"""
        try:
            old_pricing = self.get_model_pricing(model_name)
            
            if model_name not in self.config["models"]:
                self.config["models"][model_name] = {}
            
            # 记录旧值
            old_input = old_pricing.get("input_per_1k", 0)
            old_output = old_pricing.get("output_per_1k", 0)
            
            # 更新配置
            self.config["models"][model_name].update({
                "input_per_1k": float(input_price),
                "output_per_1k": float(output_price),
                "currency": currency or old_pricing.get("currency", "USD"),
                "provider": provider or old_pricing.get("provider", "Unknown"),
                "last_updated": datetime.now().isoformat()
            })
            
            # 记录历史
            if old_input != input_price or old_output != output_price:
                self.config["history"].append({
                    "date": datetime.now().isoformat(),
                    "model": model_name,
                    "old_input": old_input,
                    "new_input": float(input_price),
                    "old_output": old_output,
                    "new_output": float(output_price),
                    "currency": currency or old_pricing.get("currency", "USD"),
                    "reason": reason or "手动修改"
                })
                # 只保留最近 50 条历史
                self.config["history"] = self.config["history"][-50:]
            
            self._save_config(self.config)
            return True
        except Exception as e:
            print(f"更新定价失败: {e}")
            return False
    
    def delete_model_pricing(self, model_name: str) -> bool:
        """删除模型定价"""
        if model_name in self.config["models"] and model_name != "default":
            del self.config["models"][model_name]
            self._save_config(self.config)
            return True
        return False
    
    def calculate_cost(self, model: str, input_tokens: int, 
                      output_tokens: int) -> dict:
        """计算 Token 成本"""
        pricing = self.get_model_pricing(model)
        
        input_cost_orig = (input_tokens / 1000) * pricing["input_per_1k"]
        output_cost_orig = (output_tokens / 1000) * pricing["output_per_1k"]
        total_orig = input_cost_orig + output_cost_orig
        
        model_currency = pricing["currency"]
        display_currency = self.config.get("currency", "CNY")
        
        # 货币转换
        if model_currency != display_currency:
            rate = self._get_exchange_rate(model_currency, display_currency)
            input_cost = input_cost_orig * rate
            output_cost = output_cost_orig * rate
            total = total_orig * rate
        else:
            input_cost = input_cost_orig
            output_cost = output_cost_orig
            total = total_orig
            rate = 1.0
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total, 6),
            "currency": display_currency,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "original_currency": model_currency,
            "exchange_rate": rate
        }
    
    def _get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """获取汇率"""
        if from_currency == to_currency:
            return 1.0
        
        rates = self.config.get("exchange_rate", {})
        
        if from_currency == "USD" and to_currency == "CNY":
            return rates.get("USD_TO_CNY", 7.25)
        elif from_currency == "CNY" and to_currency == "USD":
            return rates.get("CNY_TO_USD", 0.1379)
        
        return 1.0
    
    def set_display_currency(self, currency: str) -> bool:
        """设置显示货币"""
        if currency in ["CNY", "USD"]:
            self.config["currency"] = currency
            self._save_config(self.config)
            return True
        return False
    
    def update_exchange_rate(self, rate: float = None) -> dict:
        """更新汇率"""
        result = {"success": False, "rate": None, "source": "manual"}
        
        try:
            if rate is None and self.config["exchange_rate"].get("auto_update"):
                # 尝试从 API 获取最新汇率
                try:
                    resp = requests.get(
                        "https://api.exchangerate-api.com/v4/latest/USD",
                        timeout=5
                    )
                    data = resp.json()
                    rate = data["rates"]["CNY"]
                    result["source"] = "api"
                except Exception as e:
                    print(f"获取汇率失败: {e}，使用默认汇率")
                    rate = 7.25
                    result["source"] = "default"
            
            if rate and rate > 0:
                self.config["exchange_rate"]["USD_TO_CNY"] = float(rate)
                self.config["exchange_rate"]["CNY_TO_USD"] = round(1 / float(rate), 6)
                self.config["exchange_rate"]["last_updated"] = datetime.now().isoformat()
                self._save_config(self.config)
                result["success"] = True
                result["rate"] = float(rate)
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_all_pricing(self) -> dict:
        """获取所有定价信息"""
        return {
            "currency": self.config.get("currency", "CNY"),
            "exchange_rate": self.config.get("exchange_rate", {}),
            "models": self.config.get("models", {}),
            "history": self.config.get("history", [])[-20:]  # 最近 20 条
        }
    
    def reset_to_default(self) -> bool:
        """重置为默认定价"""
        try:
            self.config["models"] = self.DEFAULT_PRICING.copy()
            self.config["history"].append({
                "date": datetime.now().isoformat(),
                "model": "ALL",
                "action": "reset_to_default",
                "reason": "用户重置"
            })
            self._save_config(self.config)
            return True
        except Exception as e:
            print(f"重置定价失败: {e}")
            return False
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        models = self.config.get("models", {})
        return [k for k in models.keys() if k != "default"]
