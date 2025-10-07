import os
from flask import Flask, jsonify
from config import logger, PORT
from routes import routes_bp  # 导入包含评论路由的蓝图
from models.user import User  # 用于创建默认管理员

# -------------------------- 创建Flask应用（保留全局CORS）--------------------------
app = Flask(__name__)


# 全局CORS处理（与原代码完全一致）
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


# -------------------------- 注册路由并添加调试日志 --------------------------
# 注册蓝图（包含所有路由）
app.register_blueprint(routes_bp)

# 新增：打印所有已注册路由（2.docx要求的调试日志）
with app.app_context():
    try:
        # 获取所有路由规则并格式化
        all_routes = [rule.rule for rule in app.url_map.iter_rules()]
        # 按路径排序，便于查看
        all_routes.sort()
        logger.info(f"2.docx - 所有已注册路由（共{len(all_routes)}条）: {all_routes}")
    except Exception as e:
        logger.error(f"2.docx - 获取路由列表失败: {str(e)}", exc_info=True)


# -------------------------- 基础路由（复刻原代码）--------------------------
@app.route("/", methods=["GET"])
def index():
    """根路由：返回服务运行状态"""
    return jsonify({"message": "Backend is running"}), 200


@app.route('/health', methods=["GET"])
def health_check():
    """健康检查路由：用于服务监控"""
    return 'OK', 200


# -------------------------- 应用初始化 --------------------------
def init_app():
    """应用初始化：创建默认管理员并检查数据"""
    try:
        success, msg = User.create_admin()
        if success:
            logger.info(f"管理员初始化完成: {msg}")
        else:
            logger.warning(f"管理员初始化警告: {msg}")

        # 检查图书数据
        from models.book import Book
        has_books = Book.check_table_data()
        if not has_books:
            logger.warning("⚠️ 图书表中没有数据，可能需要初始化数据")

    except Exception as e:
        logger.error(f"应用初始化失败: {str(e)}", exc_info=True)
        raise  # 初始化失败时终止启动


# -------------------------- 启动入口 --------------------------
if __name__ == "__main__":
    init_app()  # 初始化应用

    # 启动服务
    logger.info(f"应用启动中: 端口={PORT}, 地址=0.0.0.0:{PORT}")
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False  # 生产环境关闭debug
    )
