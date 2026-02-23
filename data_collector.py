"""
OpenClaw Monitor - Data Collector
收集 OpenClaw 状态、系统信息、任务数据等
"""

import os
import json
import glob
import psutil
import socket
import platform
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests


class OpenClawCollector:
    """OpenClaw 数据收集器"""
    
    def __init__(self):
        self.home_dir = os.path.expanduser("~")
        self.openclaw_dir = os.path.join(self.home_dir, ".openclaw")
        self.config_file = os.path.join(self.openclaw_dir, "openclaw.json")
        self.workspace_dir = os.path.join(self.openclaw_dir, "workspace")
        self.agents_dir = os.path.join(self.openclaw_dir, "agents")
        self.logs_dir = os.path.join(self.openclaw_dir, "logs")
        self.tmp_logs = "/tmp/openclaw"
    
    def get_openclaw_version(self) -> dict:
        """获取 OpenClaw 版本信息"""
        version_info = {
            "current": "unknown",
            "latest": "unknown",
            "update_available": False,
            "last_checked": None
        }
        
        try:
            # 从配置文件读取
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    version_info["current"] = config.get("meta", {}).get("lastTouchedVersion", "unknown")
            
            # 尝试执行命令获取版本
            try:
                result = subprocess.run(
                    ["openclaw", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version_info["current"] = result.stdout.strip()
            except:
                pass
            
            # 检查最新版本（npm registry）
            try:
                resp = requests.get(
                    "https://registry.npmjs.org/openclaw/latest",
                    timeout=5
                )
                latest = resp.json().get("version", "unknown")
                version_info["latest"] = latest
                version_info["update_available"] = latest != version_info["current"]
                version_info["last_checked"] = datetime.now().isoformat()
            except:
                pass
                
        except Exception as e:
            print(f"获取版本信息失败: {e}")
        
        return version_info
    
    def get_gateway_status(self) -> dict:
        """获取 Gateway 状态"""
        status = {
            "online": False,
            "version": "unknown",
            "port": 18789,
            "uptime_seconds": 0,
            "last_error": None
        }
        
        try:
            # 检查端口是否监听
            for conn in psutil.net_connections():
                if conn.laddr.port == 18789:
                    status["online"] = True
                    break
            
            # 尝试获取 Gateway 信息
            try:
                resp = requests.get("http://127.0.0.1:18789/health", timeout=2)
                if resp.status_code == 200:
                    status["online"] = True
            except:
                pass
            
            # 获取进程运行时间
            for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cmdline']):
                try:
                    if 'openclaw' in ' '.join(proc.info['cmdline'] or []).lower():
                        create_time = datetime.fromtimestamp(proc.info['create_time'])
                        status["uptime_seconds"] = (datetime.now() - create_time).total_seconds()
                        break
                except:
                    continue
                    
        except Exception as e:
            status["last_error"] = str(e)
        
        return status
    
    def get_system_info(self) -> dict:
        """获取系统信息"""
        try:
            # 获取 IP 地址
            hostname = socket.gethostname()
            try:
                ip = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
            except:
                ip = "127.0.0.1"
            
            # 获取 CPU 信息
            cpu_info = {
                "count": psutil.cpu_count(),
                "percent": psutil.cpu_percent(interval=1),
                "freq": psutil.cpu_freq().current if psutil.cpu_freq() else 0
            }
            
            # 获取内存信息
            mem = psutil.virtual_memory()
            mem_info = {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "percent": mem.percent
            }
            
            # 获取磁盘信息
            disk = psutil.disk_usage('/')
            disk_info = {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            }
            
            return {
                "hostname": hostname,
                "platform": platform.platform(),
                "os": platform.system(),
                "architecture": platform.machine(),
                "ip": ip,
                "cpu": cpu_info,
                "memory": mem_info,
                "disk": disk_info,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_running_tasks(self) -> dict:
        """获取运行中的任务"""
        tasks = {
            "running": 0,
            "pending": 0,
            "completed_24h": 0,
            "tasks": []
        }
        
        try:
            sessions_dir = os.path.join(self.agents_dir, "main", "sessions")
            if not os.path.exists(sessions_dir):
                return tasks
            
            now = datetime.now()
            
            for session_file in glob.glob(f"{sessions_dir}/*.jsonl"):
                try:
                    # 获取文件修改时间
                    mtime = datetime.fromtimestamp(os.path.getmtime(session_file))
                    
                    # 读取最后几行判断状态
                    with open(session_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if not lines:
                            continue
                        
                        # 解析最后一条记录
                        try:
                            last_record = json.loads(lines[-1])
                        except:
                            continue
                        
                        # 简单的状态判断
                        is_active = (now - mtime).total_seconds() < 3600  # 1小时内活跃
                        
                        # 提取模型信息
                        model = "unknown"
                        for line in reversed(lines):
                            try:
                                record = json.loads(line)
                                if record.get("type") == "model_change":
                                    model = record.get("modelId", "unknown")
                                    break
                            except:
                                continue
                        
                        task_info = {
                            "id": os.path.basename(session_file).replace('.jsonl', '')[:8],
                            "file": os.path.basename(session_file),
                            "model": model,
                            "status": "running" if is_active else "completed",
                            "last_active": mtime.isoformat(),
                            "duration_minutes": int((now - mtime).total_seconds() / 60)
                        }
                        
                        if is_active:
                            tasks["running"] += 1
                            tasks["tasks"].append(task_info)
                        elif (now - mtime).total_seconds() < 86400:  # 24小时内
                            tasks["completed_24h"] += 1
                            
                except Exception as e:
                    continue
            
            # 按时间排序
            tasks["tasks"].sort(key=lambda x: x["last_active"], reverse=True)
            
        except Exception as e:
            print(f"获取任务失败: {e}")
        
        return tasks
    
    def get_token_usage(self, days: int = 7) -> dict:
        """获取 Token 使用统计"""
        usage = {
            "today": {"input": 0, "output": 0, "total": 0, "cost": 0},
            "week": {"input": 0, "output": 0, "total": 0, "cost": 0},
            "month": {"input": 0, "output": 0, "total": 0, "cost": 0},
            "daily": [],
            "total_sessions": 0
        }
        
        try:
            sessions_dir = os.path.join(self.agents_dir, "main", "sessions")
            if not os.path.exists(sessions_dir):
                return usage
            
            today = datetime.now().date()
            daily_data = {}
            total_sessions = 0
            
            for session_file in glob.glob(f"{sessions_dir}/*.jsonl"):
                try:
                    file_date = datetime.fromtimestamp(
                        os.path.getmtime(session_file)
                    ).date()
                    
                    # 只读取最近的数据
                    if (today - file_date).days > days:
                        continue
                    
                    date_str = file_date.isoformat()
                    if date_str not in daily_data:
                        daily_data[date_str] = {"input": 0, "output": 0, "total": 0, "cost": 0}
                    
                    # 解析文件中的 token 使用
                    session_input = 0
                    session_output = 0
                    
                    with open(session_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                record = json.loads(line)
                                if record.get("type") == "message":
                                    message = record.get("message", {})
                                    if message.get("role") == "assistant":
                                        usage_data = message.get("usage", {})
                                        if usage_data:
                                            # 支持多种格式
                                            input_tokens = usage_data.get("input", 0) or usage_data.get("input_tokens", 0)
                                            output_tokens = usage_data.get("output", 0) or usage_data.get("output_tokens", 0)
                                            total_tokens = usage_data.get("totalTokens", 0) or (input_tokens + output_tokens)
                                            
                                            session_input += input_tokens
                                            session_output += output_tokens
                                            
                                            # 累加到每日统计
                                            daily_data[date_str]["input"] += input_tokens
                                            daily_data[date_str]["output"] += output_tokens
                                            daily_data[date_str]["total"] += total_tokens
                            except:
                                continue
                    
                    if session_input > 0 or session_output > 0:
                        total_sessions += 1
                                
                except Exception as e:
                    continue
            
            # 汇总数据
            today_str = today.isoformat()
            for date_str, data in daily_data.items():
                if date_str == today_str:
                    usage["today"] = data
                usage["week"]["input"] += data["input"]
                usage["week"]["output"] += data["output"]
                usage["week"]["total"] += data["total"]
                usage["month"]["input"] += data["input"]
                usage["month"]["output"] += data["output"]
                usage["month"]["total"] += data["total"]
            
            usage["total_sessions"] = total_sessions
            
            # 转换为列表格式用于图表
            usage["daily"] = [
                {"date": d, **data}
                for d, data in sorted(daily_data.items())
            ]
            
        except Exception as e:
            print(f"获取 Token 使用失败: {e}")
        
        return usage
    
    def get_error_logs(self, days: int = 7) -> List[dict]:
        """获取错误日志"""
        errors = []
        error_patterns = [
            "error", "fail", "timeout", "refused", "blocked",
            "invalid", "expired", "unauthorized", "exception"
        ]
        
        try:
            # 检查日志文件
            log_files = []
            
            # /tmp/openclaw 日志
            if os.path.exists(self.tmp_logs):
                log_files.extend(glob.glob(f"{self.tmp_logs}/*.log"))
            
            # 读取日志
            now = datetime.now()
            error_counts = {}
            
            for log_file in log_files:
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                    if (now - mtime).days > days:
                        continue
                    
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line_lower = line.lower()
                            for pattern in error_patterns:
                                if pattern in line_lower:
                                    # 提取错误信息
                                    error_key = line.strip()[:100]
                                    if error_key in error_counts:
                                        error_counts[error_key]["count"] += 1
                                    else:
                                        error_counts[error_key] = {
                                            "message": line.strip()[:200],
                                            "count": 1,
                                            "time": mtime.isoformat(),
                                            "level": "error" if "error" in line_lower else "warning"
                                        }
                                    break
                except:
                    continue
            
            # 转换为列表并排序
            errors = sorted(
                error_counts.values(),
                key=lambda x: x["count"],
                reverse=True
            )[:10]  # 只返回前 10 个
            
        except Exception as e:
            print(f"获取错误日志失败: {e}")
        
        return errors
    
    def get_summary(self) -> dict:
        """获取完整汇总数据"""
        return {
            "timestamp": datetime.now().isoformat(),
            "version": self.get_openclaw_version(),
            "gateway": self.get_gateway_status(),
            "system": self.get_system_info(),
            "tasks": self.get_running_tasks(),
            "token_usage": self.get_token_usage(),
            "errors": self.get_error_logs()
        }
