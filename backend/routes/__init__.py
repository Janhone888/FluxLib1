from flask import Blueprint
import logging

logger = logging.getLogger()

# 1. 创建唯一蓝图实例（全局共用）
routes_bp = Blueprint('fluxlib_routes', __name__)


def register_all_routes():
    """注册所有路由并返回蓝图"""
    logger.info("🚀 开始注册所有路由...")

    # 必须导入并注册图书路由（优先处理）
    try:
        from .book_routes import register_book_routes
        register_book_routes(routes_bp)
        logger.info("✅ 图书路由注册成功")
    except ImportError as e:
        logger.error(f"❌ 图书路由注册函数导入失败: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"❌ 图书路由注册过程出错: {str(e)}", exc_info=True)
        raise

    # 2. 导入其他核心路由注册函数
    try:
        # 核心路由：认证、借阅、用户、公告、评论、AI、预约
        from .auth_routes import register_auth_routes
        from .borrow_routes import register_borrow_routes
        from .user_routes import register_user_routes
        from .announcement_routes import register_announcement_routes
        from .comments_routes import register_comments_routes
        from .ai_routes import register_ai_routes
        from .reservation_routes import register_reservation_routes  # 新增
        logger.info("✅ 其他路由注册函数导入成功")
    except ImportError as e:
        logger.error(f"❌ 其他路由函数导入失败: {str(e)}", exc_info=True)
        raise

    # 3. 注册其他核心路由（按业务逻辑顺序）
    try:
        # 认证路由（/login, /register 等）- 必须最先注册
        logger.info("🔐 注册认证路由...")
        register_auth_routes(routes_bp)
        logger.info("✅ 认证路由注册完成")

        # 借阅路由
        logger.info("📚 注册借阅路由...")
        register_borrow_routes(routes_bp)
        logger.info("✅ 借阅路由注册完成")

        # 用户路由
        logger.info("👤 注册用户路由...")
        register_user_routes(routes_bp)
        logger.info("✅ 用户路由注册完成")

        # 公告路由
        logger.info("📢 注册公告路由...")
        register_announcement_routes(routes_bp)
        logger.info("✅ 公告路由注册完成")

        # 评论路由
        logger.info("💬 注册评论路由...")
        register_comments_routes(routes_bp)
        logger.info("✅ 评论路由注册完成")

        # 新增AI路由注册
        logger.info("🤖 注册AI路由...")
        register_ai_routes(routes_bp)
        logger.info("✅ AI路由注册完成")

        # 预约路由
        logger.info("📅 注册预约路由...")
        register_reservation_routes(routes_bp)
        logger.info("✅ 预约路由注册完成")

        logger.info("🎉 所有核心路由注册完成")
    except Exception as e:
        logger.error(f"❌ 路由注册失败: {str(e)}", exc_info=True)
        raise

    return routes_bp


# 立即执行路由注册
routes_bp = register_all_routes()

# 4. 导出蓝图（供main.py注册到应用）
__all__ = ['routes_bp']
globals()['routes_bp'] = routes_bp
