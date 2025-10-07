from flask import request, jsonify
from services.auth_service import send_verification_email, register_user, login_user
from config import logger


def register_auth_routes(bp):
    """注册认证相关路由到蓝图"""

    @bp.route('/send-verification-code', methods=['POST'])
    def handle_send_verification_code():
        """发送注册验证码（对应原代码同名路由）"""
        try:
            data = request.get_json()
            email = data.get('email')
            if not email:
                return jsonify({'error': 'Email is required'}), 400
            # 调用认证服务
            success, msg = send_verification_email(email)
            if success:
                return jsonify({'message': msg}), 200
            else:
                return jsonify({'error': msg}), 500
        except Exception as e:
            logger.error(f"处理验证码发送失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to send verification code'}), 500

    @bp.route('/register', methods=['POST'])
    def handle_register():
        """用户注册（对应原代码同名路由）"""
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            code = data.get('code')
            gender = data.get('gender')  # 可选字段
            # 校验必填参数
            if not email or not password or not code:
                return jsonify({'error': 'Email, password and code are required'}), 400
            # 调用认证服务
            success, result = register_user(email, password, code, gender)
            if success:
                return jsonify({'user_id': result}), 201
            else:
                return jsonify({'error': result}), 400
        except Exception as e:
            logger.error(f"处理注册失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Registration failed'}), 500

    @bp.route('/login', methods=['POST'])
    def handle_login():
        """用户登录（对应原代码同名路由，含临时管理员权限）"""
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            admin_code = data.get('admin_code')  # 可选：管理员码
            # 校验必填参数
            if not email or not password:
                return jsonify({'error': '邮箱和密码是必填项'}), 400
            # 调用认证服务
            success, result = login_user(email, password, admin_code)
            if success:
                # 生成Token（与原代码一致：用user_id作为Token）
                token = result['user_id']
                return jsonify({
                    'token': token,
                    'user_id': result['user_id'],
                    'email': email,
                    'role': result['role'],
                    'is_admin': result.get('is_admin', False)
                }), 200
            else:
                # 管理员码错误返回403，其他错误返回401
                if result == "管理员码错误":
                    return jsonify({'error': result}), 403
                else:
                    return jsonify({'error': result}), 401
        except Exception as e:
            logger.error(f"处理登录失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Login failed'}), 500