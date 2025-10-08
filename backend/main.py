import os
from flask import Flask, jsonify
from config import logger, PORT
from routes import routes_bp  # 导入包含所有路由（认证、图书、借阅等）的蓝图
from models.user import User  # 用于创建默认管理员

# -------------------------- 创建Flask应用（保留全局CORS）--------------------------
app = Flask(__name__)


# 全局CORS处理（与原代码完全一致，确保跨域请求正常）
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


# -------------------------- 注册路由并添加调试日志 --------------------------
# 注册蓝图（一次性加载所有已配置的路由）
app.register_blueprint(routes_bp)

# 新增：详细打印所有已注册路由（含请求方法、路径，便于调试核对）
with app.app_context():
    try:
        # 遍历所有路由规则，整理关键信息（排除OPTIONS/HEAD默认方法）
        all_routes = []
        for rule in app.url_map.iter_rules():
            # 筛选有效请求方法（移除框架默认的OPTIONS和HEAD）
            valid_methods = sorted(rule.methods - {'OPTIONS', 'HEAD'})
            # 格式化路由信息为字典
            all_routes.append({
                'endpoint': rule.endpoint,  # 路由端点名
                'methods': ','.join(valid_methods),  # 支持的请求方法（逗号分隔）
                'path': rule.rule  # 路由路径
            })

        # 按路由路径排序，提升可读性
        all_routes.sort(key=lambda x: x['path'])

        # 打印路由汇总日志
        logger.info(f"📋 所有已注册路由（共{len(all_routes)}条）:")
        # 逐条打印路由详情（方法占6字符对齐，路径左对齐）
        for route in all_routes:
            logger.info(f"  {route['methods']:6} | {route['path']}")

    except Exception as e:
        logger.error(f"❌ 获取路由列表失败: {str(e)}", exc_info=True)


# -------------------------- 基础路由（复刻原代码，确保服务可用性）--------------------------
@app.route("/", methods=["GET"])
def index():
    """根路由：返回服务运行状态（供前端/测试快速验证）"""
    return jsonify({"message": "Backend is running"}), 200


@app.route('/health', methods=["GET"])
def health_check():
    """健康检查路由：用于服务监控（如Docker、K8s等调度系统检测）"""
    return 'OK', 200


# -------------------------- 应用初始化（管理员+数据检查）--------------------------
def init_app():
    """应用启动前初始化：创建默认管理员、检查核心数据表状态"""
    try:
        # 1. 初始化默认管理员
        success, msg = User.create_admin()
        if success:
            logger.info(f"✅ 管理员初始化完成: {msg}")
        else:
            logger.warning(f"⚠️ 管理员初始化警告: {msg}")

        # 2. 检查图书表数据状态（避免无数据导致功能异常）
        logger.info("🔍 开始检查图书表数据状态...")
        from models.book import Book  # 延迟导入，避免初始化顺序问题
        has_books = Book.check_table_data()
        if not has_books:
            logger.warning("⚠️ 图书表中没有数据，请运行数据初始化脚本（如init_book_data.py）")
        else:
            logger.info("✅ 图书表检测到有效数据，可正常提供图书相关功能")

    except Exception as e:
        logger.error(f"❌ 应用初始化失败: {str(e)}", exc_info=True)
        raise  # 初始化失败时强制终止启动，避免带病运行


# -------------------------- 应用启动入口 --------------------------
if __name__ == "__main__":
    init_app()  # 先执行初始化（管理员创建+数据检查）

    # 启动Flask服务
    logger.info(f"🚀 应用启动中: 端口={PORT}, 访问地址=http://0.0.0.0:{PORT}")
    app.run(
        host='0.0.0.0',  # 允许外部设备访问（如同一局域网内的前端）
        port=PORT,  # 端口从配置文件读取，便于环境切换
        debug=False  # 生产环境关闭Debug模式，避免安全风险
    )
