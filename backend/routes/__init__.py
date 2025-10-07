# 2.docx > Code/routes/__init__.py（完整路由注册版）
from flask import Blueprint
import logging

logger = logging.getLogger()

# 1. 创建唯一蓝图实例（全局共用）
routes_bp = Blueprint('fluxlib_routes', __name__)

# 必须导入并注册图书路由（优先处理，确保在app.register_blueprint前完成）
try:
    from .book_routes import register_book_routes

    register_book_routes(routes_bp)
    logger.info("2.docx - 图书路由注册成功")
except ImportError as e:
    logger.error(f"2.docx - 图书路由注册函数导入失败: {str(e)}", exc_info=True)
    raise  # 图书路由为核心必需，导入失败强制终止
except Exception as e:
    logger.error(f"2.docx - 图书路由注册过程出错: {str(e)}", exc_info=True)
    raise  # 图书路由注册失败强制终止

# 2. 导入其他核心路由注册函数
try:
    # 核心路由：借阅、用户、公告
    from .borrow_routes import register_borrow_routes
    from .user_routes import register_user_routes
    from .announcement_routes import register_announcement_routes
    # 新增路由：评论
    from .comments_routes import register_comments_routes

    logger.info("2.docx - 其他路由注册函数导入成功")
except ImportError as e:
    logger.error(f"2.docx - 其他路由函数导入失败: {str(e)}", exc_info=True)
    raise

# 3. 注册其他核心路由（按业务逻辑顺序）
try:
    # 借阅路由（/books/<book_id>/borrow、/user/borrows等）
    register_borrow_routes(routes_bp)
    # 用户路由（/user/current、/favorites、/history等）
    register_user_routes(routes_bp)
    # 公告路由（/announcements等）
    register_announcement_routes(routes_bp)
    # 评论路由（/books/<book_id>/comments等）
    register_comments_routes(routes_bp)
    logger.info("2.docx - 所有其他核心路由注册完成")
except Exception as e:
    logger.error(f"2.docx - 其他路由注册失败: {str(e)}", exc_info=True)
    raise

# 4. 导出蓝图（供main.py注册到应用）
__all__ = ['routes_bp']
globals()['routes_bp'] = routes_bp
