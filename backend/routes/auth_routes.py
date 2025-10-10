from flask import request, jsonify
from services.auth_service import (
    send_verification_email, register_user, login_user,
    send_reset_password_code, reset_password, verify_reset_code  # 新增导入verify_reset_code
)
from config import logger


def register_auth_routes(bp):
    """注册认证相关路由到蓝图（含登录、注册、忘记密码功能）"""

    @bp.route('/send-verification-code', methods=['POST'])
    def handle_send_verification_code():
        """发送注册验证码（供用户注册时使用）"""
        try:
            data = request.get_json()
            email = data.get('email')
            if not email:
                return jsonify({'error': 'Email is required'}), 400
            # 调用认证服务发送注册验证码
            success, msg = send_verification_email(email)
            if success:
                return jsonify({'message': msg}), 200
            else:
                return jsonify({'error': msg}), 500
        except Exception as e:
            logger.error(f"处理注册验证码发送失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to send verification code'}), 500

    @bp.route('/register', methods=['POST'])
    def handle_register():
        """用户注册接口（需验证注册验证码）"""
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            code = data.get('code')
            gender = data.get('gender')  # 可选：用户性别
            # 校验必填参数
            if not email or not password or not code:
                return jsonify({'error': 'Email, password and code are required'}), 400
            # 调用认证服务完成注册
            success, result = register_user(email, password, code, gender)
            if success:
                return jsonify({'user_id': result}), 201  # 201表示资源创建成功
            else:
                return jsonify({'error': result}), 400
        except Exception as e:
            logger.error(f"处理用户注册失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Registration failed'}), 500

    @bp.route('/login', methods=['POST'])
    def handle_login():
        """用户登录接口（支持普通用户/管理员临时权限）"""
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            admin_code = data.get('admin_code')  # 可选：管理员临时权限码
            # 校验必填参数
            if not email or not password:
                return jsonify({'error': '邮箱和密码是必填项'}), 400
            # 调用认证服务完成登录
            success, result = login_user(email, password, admin_code)
            if success:
                # 生成Token（沿用原有逻辑：以user_id作为Token）
                token = result['user_id']
                return jsonify({
                    'token': token,
                    'user_id': result['user_id'],
                    'email': email,
                    'role': result['role'],
                    'is_admin': result.get('is_admin', False)
                }), 200
            else:
                # 管理员码错误返回403（权限不足），其他错误返回401（未授权）
                if result == "管理员码错误":
                    return jsonify({'error': result}), 403
                else:
                    return jsonify({'error': result}), 401
        except Exception as e:
            logger.error(f"处理用户登录失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Login failed'}), 500

    @bp.route('/forgot-password/send-code', methods=['POST'])
    def handle_send_reset_code():
        """发送重置密码验证码（供忘记密码时使用）"""
        try:
            data = request.get_json()
            email = data.get('email')
            if not email:
                return jsonify({'error': '邮箱是必填项'}), 400
            # 调用认证服务发送密码重置验证码
            success, msg = send_reset_password_code(email)
            if success:
                return jsonify({'message': msg}), 200
            else:
                return jsonify({'error': msg}), 400
        except Exception as e:
            logger.error(f"处理重置密码验证码发送失败: {str(e)}", exc_info=True)
            return jsonify({'error': '发送验证码失败'}), 500

    # 新增：验证重置密码验证码路由
    @bp.route('/forgot-password/verify-code', methods=['POST'])
    def handle_verify_reset_code():
        """验证重置密码验证码（新增独立验证接口）"""
        try:
            data = request.get_json()
            email = data.get('email')
            code = data.get('code')

            if not email or not code:
                return jsonify({'error': '邮箱和验证码是必填项'}), 400

            # 调用独立的验证码验证服务
            verify_success, verify_msg = verify_reset_code(email, code)
            if not verify_success:
                return jsonify({'error': verify_msg}), 400

            return jsonify({'success': True, 'message': '验证码验证成功'}), 200

        except Exception as e:
            logger.error(f"验证重置密码验证码失败: {str(e)}")
            return jsonify({'error': '验证失败'}), 500

    @bp.route('/forgot-password/reset', methods=['POST'])
    def handle_reset_password():
        """密码重置接口（需验证重置密码验证码）"""
        try:
            data = request.get_json()
            email = data.get('email')
            code = data.get('code')
            new_password = data.get('new_password')
            # 校验必填参数（邮箱、验证码、新密码缺一不可）
            if not email or not code or not new_password:
                return jsonify({'error': '邮箱、验证码和新密码是必填项'}), 400
            # 调用认证服务完成密码重置
            success, msg = reset_password(email, code, new_password)
            if success:
                return jsonify({'message': msg}), 200
            else:
                return jsonify({'error': msg}), 400
        except Exception as e:
            logger.error(f"处理密码重置失败: {str(e)}", exc_info=True)
            return jsonify({'error': '重置密码失败'}), 500