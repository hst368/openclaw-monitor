"""
OpenClaw Monitor - Web Dashboard (Secure Version)
添加基础身份验证的监控面板
"""

import os
import sys
import base64
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS

# 导入自定义模块
from pricing_manager import PricingManager
from data_collector import OpenClawCollector

app = Flask(__name__)
CORS(app)

# ===== 安全配置 =====
# 从环境变量读取密码，默认为 admin/admin123
# 建议修改：export MONITOR_USERNAME=yourname
#          export MONITOR_PASSWORD=yourpassword
AUTH_USERNAME = os.environ.get('MONITOR_USERNAME', 'admin')
AUTH_PASSWORD = os.environ.get('MONITOR_PASSWORD', 'admin123')

# 全局实例
pricing_mgr = PricingManager()
data_collector = OpenClawCollector()

# 配置
APP_VERSION = "1.0.0-secure"
HOST = "0.0.0.0"
PORT = 8081


def check_auth(username, password):
    """验证用户名密码"""
    return username == AUTH_USERNAME and password == AUTH_PASSWORD


def authenticate():
    """返回 401 响应"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    """装饰器：需要身份验证"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            return authenticate()
        
        try:
            auth_type, auth_string = auth.split(' ', 1)
            if auth_type.lower() != 'basic':
                return authenticate()
            
            decoded = base64.b64decode(auth_string).decode('utf-8')
            username, password = decoded.split(':', 1)
        except Exception:
            return authenticate()
        
        if not check_auth(username, password):
            return authenticate()
        
        return f(*args, **kwargs)
    return decorated


# 只对 API 和数据页面要求认证，静态资源可公开
@app.route('/')
@requires_auth
def index():
    """主页面"""
    return render_template('index.html')


# ========== API 路由（全部需要认证） ==========

@app.route('/api/summary')
@requires_auth
def api_summary():
    """获取完整概览数据"""
    try:
        data = data_collector.get_summary()
        data["monitor_version"] = APP_VERSION
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/status')
@requires_auth
def api_status():
    """获取基本状态"""
    try:
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "gateway": data_collector.get_gateway_status(),
            "tasks": {
                "running": data_collector.get_running_tasks()["running"]
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/pricing', methods=['GET'])
@requires_auth
def get_pricing():
    """获取定价配置"""
    return jsonify(pricing_mgr.get_all_pricing())


@app.route('/api/pricing', methods=['POST'])
@requires_auth
def update_pricing():
    """更新模型定价"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    model = data.get('model')
    input_price = data.get('input_per_1k')
    output_price = data.get('output_per_1k')
    currency = data.get('currency', 'CNY')
    provider = data.get('provider', '')
    reason = data.get('reason', '')
    
    if not model or input_price is None or output_price is None:
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    success = pricing_mgr.update_model_pricing(
        model, float(input_price), float(output_price),
        currency, provider, reason
    )
    
    return jsonify({"success": success})


@app.route('/api/pricing/model/<model_name>', methods=['DELETE'])
@requires_auth
def delete_model_pricing(model_name):
    """删除模型定价"""
    success = pricing_mgr.delete_model_pricing(model_name)
    return jsonify({"success": success})


@app.route('/api/pricing/currency', methods=['PUT'])
@requires_auth
def set_currency():
    """设置显示货币"""
    data = request.json
    currency = data.get('currency')
    if currency in ['CNY', 'USD']:
        success = pricing_mgr.set_display_currency(currency)
        return jsonify({"success": success})
    return jsonify({"success": False, "error": "Invalid currency"}), 400


@app.route('/api/pricing/exchange-rate', methods=['GET'])
@requires_auth
def get_exchange_rate():
    """获取当前汇率"""
    config = pricing_mgr.get_all_pricing()
    return jsonify(config.get('exchange_rate', {}))


@app.route('/api/pricing/exchange-rate', methods=['POST'])
@requires_auth
def update_exchange_rate():
    """更新汇率"""
    data = request.json
    rate = data.get('rate') if data else None
    result = pricing_mgr.update_exchange_rate(rate)
    return jsonify(result)


@app.route('/api/pricing/reset', methods=['POST'])
@requires_auth
def reset_pricing():
    """重置为默认定价"""
    success = pricing_mgr.reset_to_default()
    return jsonify({"success": success})


@app.route('/api/pricing/calculate', methods=['POST'])
@requires_auth
def calculate_cost():
    """计算 Token 成本"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    model = data.get('model', 'default')
    input_tokens = data.get('input_tokens', 0)
    output_tokens = data.get('output_tokens', 0)
    
    result = pricing_mgr.calculate_cost(model, input_tokens, output_tokens)
    return jsonify(result)


@app.route('/api/tasks')
@requires_auth
def get_tasks():
    """获取任务列表"""
    return jsonify(data_collector.get_running_tasks())


@app.route('/api/logs')
@requires_auth
def get_logs():
    """获取错误日志"""
    days = request.args.get('days', 7, type=int)
    return jsonify(data_collector.get_error_logs(days))


@app.route('/api/system')
@requires_auth
def get_system():
    """获取系统信息"""
    return jsonify(data_collector.get_system_info())


@app.route('/api/version')
@requires_auth
def get_version():
    """获取版本信息"""
    return jsonify({
        "monitor": APP_VERSION,
        "openclaw": data_collector.get_openclaw_version()
    })


@app.route('/api/token-usage')
@requires_auth
def get_token_usage():
    """获取 Token 使用统计"""
    days = request.args.get('days', 7, type=int)
    usage = data_collector.get_token_usage(days)
    
    # 添加成本计算
    if 'daily' in usage:
        for day in usage['daily']:
            cost = pricing_mgr.calculate_cost(
                'default',
                day.get('input', 0),
                day.get('output', 0)
            )
            day['cost'] = cost['total_cost']
            day['currency'] = cost['currency']
    
    return jsonify(usage)


@app.route('/api/health')
def health():
    """健康检查端点（无需认证）"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": APP_VERSION,
        "secure": True
    })


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           OpenClaw Monitor {APP_VERSION}                     ║
║           🔒 安全版本（已启用身份验证）                    ║
╠══════════════════════════════════════════════════════════╣
║  默认账号: {AUTH_USERNAME:<20}                     ║
║  默认密码: {'*' * len(AUTH_PASSWORD):<20}                     ║
╠══════════════════════════════════════════════════════════╣
║  修改密码: export MONITOR_PASSWORD=yourpassword          ║
╠══════════════════════════════════════════════════════════╣
║  Starting server...                                      ║
║                                                          ║
║  Local:   http://127.0.0.1:{PORT}                         ║
║  Network: http://0.0.0.0:{PORT}                           ║
║                                                          ║
║  Press Ctrl+C to stop                                    ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True
    )
