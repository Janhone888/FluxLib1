import os
from flask import Flask, jsonify
from config import logger, PORT
from routes import routes_bp
from models.user import User
from repositories.book_repository import BookRepository
from repositories.user_repository import UserRepository
from repositories.borrow_repository import BorrowRepository
from repositories.comment_repository import CommentRepository
from repositories.comment_like_repository import CommentLikeRepository
from repositories.favorite_repository import FavoriteRepository
from repositories.view_history_repository import ViewHistoryRepository
from repositories.announcement_repository import AnnouncementRepository

# 创建Flask应用
app = Flask(__name__)


# 全局CORS处理
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


# 注册蓝图
app.register_blueprint(routes_bp)

# 打印所有已注册路由
with app.app_context():
    try:
        all_routes = []
        for rule in app.url_map.iter_rules():
            valid_methods = sorted(rule.methods - {'OPTIONS', 'HEAD'})
            all_routes.append({
                'endpoint': rule.endpoint,
                'methods': ','.join(valid_methods),
                'path': rule.rule
            })

        all_routes.sort(key=lambda x: x['path'])
        logger.info(f"📋 所有已注册路由（共{len(all_routes)}条）:")
        for route in all_routes:
            logger.info(f" {route['methods']:6} | {route['path']}")
    except Exception as e:
        logger.error(f"❌ 获取路由列表失败: {str(e)}", exc_info=True)


# 基础路由
@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Backend is running"}), 200


@app.route('/health', methods=["GET"])
def health_check():
    return 'OK', 200


def init_app():
    """应用启动前初始化"""
    try:
        # 1. 初始化仓储层（可选：测试仓储层连接）
        book_repo = BookRepository()
        user_repo = UserRepository()
        borrow_repo = BorrowRepository()
        comment_repo = CommentRepository()
        comment_like_repo = CommentLikeRepository()
        favorite_repo = FavoriteRepository()
        view_history_repo = ViewHistoryRepository()
        announcement_repo = AnnouncementRepository()
        logger.info("✅ 仓储层初始化完成")

        # 2. 初始化默认管理员
        success, msg = User.create_admin()
        if success:
            logger.info(f"✅ 管理员初始化完成: {msg}")
        else:
            logger.warning(f"⚠️ 管理员初始化警告: {msg}")

        # 3. 检查图书表数据状态
        logger.info("🔍 开始检查图书表数据状态...")
        from models.book import Book
        has_books = Book.check_table_data()
        if not has_books:
            logger.warning("⚠️ 图书表中没有数据，请运行数据初始化脚本")
        else:
            logger.info("✅ 图书表检测到有效数据，可正常提供图书相关功能")

    except Exception as e:
        logger.error(f"❌ 应用初始化失败: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    init_app()
    logger.info(f"🚀 应用启动中: 端口={PORT}, 访问地址=http://0.0.0.0:{PORT}")
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False
    )
