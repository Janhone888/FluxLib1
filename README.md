## FluxLib泛集库

FluxLib 泛集库是一个基于阿里云服务的全栈图书管理系统，采用前后端分离架构。系统提供图书管理、借阅归还、用户管理等功能，具有高性能、可扩展和安全的特点。

可以使用外网点击https://book-mgmt-imrt93854-janhones-projects.vercel.app/，打开我们的网站。

演示视频:https://pan.baidu.com/s/1evxzun-EKBhao4pP4Q1gWA?pwd=1234



## 核心功能

### 1.用户认证系统

- 邮箱验证码注册/登录
- JWT Token认证
-  管理员账户自动创建
- 角色权限控制（用户/管理员）



### 2.图书管理

- 图书增删改查（CRUD）
- 多条件搜索（书名/作者/分类）
- 图书封面管理（OSS存储）
- 库存状态管理（可借/已借/维护中）



### 3.借阅系统

- 单本/批量借阅
- 借阅期限选择（7/15/30天）
- 借阅记录管理
- 批量归还功能



### 4.数据分析

- 借阅趋势分析
- 热门图书排行
- 分类分布统计
- 系统性能指标



## 前端组件文档

### 核心组件

### 1.ImageUploader.vue

- 图书封面上传组件
- 支持拖拽上传
- 进度显示和取消功能
- 自动生成OSS预签名URL

### 2.TopNav.vue

- 顶部导航栏
- 根据用户角色显示不同菜单
- 用户信息展示和退出功能

### 3.BookCard.vue

- 图片卡片展示组件
- 显示图书基本信息
- 状态标签和库存显示



### 页面视图

### 1.LoginView.vue

- 动态背景视频
- 登陆/注册双模式切换
- 验证码发送和倒计时

### 2.BooksView.vue

- 图书网格布局展示
- 搜索和分类筛选
- 分页功能

### 3.BookDetail.vue

- 图片详细信息展示
- 借阅/归还功能
- 借阅历史记录

### 4.BorrowManage.vue

- 用户借阅记录管理
- 单本/批量归还
- 状态筛选和排序

### 5.Analytics.vue

- 数据可视化展示
- 借阅趋势图表
- 分类分布饼图
- 热门图书排行



## 数据库设计

### 图书表(Books)

| ***\*列名\**** | 类型    | 描述       |
| -------------- | ------- | ---------- |
| book_id        | STRING  | 图书唯一ID |
| title          | STRING  | 书名       |
| author         | STRING  | 作者       |
| publisher      | STRING  | 出版社     |
| isbn           | STRING  | ISBN号     |
| price          | DOUBLE  | 价格       |
| stock          | INTEGER | 库存数量   |
| category       | STRING  | 分类       |
| cover          | STRING  | 封面url    |
| status         | STRING  | 状态       |
| created_at     | INTEGER | 创建时间戳 |
| updated_at     | INTEGER | 更新时间戳 |

## 

### 用户表

| ***\*列名\**** | 类型    | 描述        |
| -------------- | ------- | ----------- |
| email          | STRING  | 用户邮箱    |
| user_id        | STRING  | 用户ID      |
| password       | STRING  | 密码        |
| Role           | STRING  | 角色        |
| created_at     | INTEGER | I创建时间戳 |
| is_verified    | STRING  | 验证状态    |



### 借阅记录表

| 列名        | 类型    | 描述       |
| ----------- | ------- | ---------- |
| borrow_id   | STRING  | 借阅记录ID |
| book_id     | STRING  | 图书ID     |
| user_id     | STRING  | 用户ID     |
| borrow_date | INTEGER | 借阅日期   |
| due_date    | INTEGER | 应还日期   |
| return_date | INTEGER | 归还日期   |
| status      | STRING  | 状态       |



## 安装和运行

### 环境要求

**后端环境**

- Python 3.8+
- 需要安装的第三方库：
  - flask
  - tablestore
  - oss2
  - smtplib
  - uuid
  - hashlib

**前端环境**

- Node.js 14+
- npm 或 yarn



### 快速开始

1.**启动服务器**：

配置环境变量

```bash
export OTS_INSTANCE_NAME=book-mgmt-ots
export OTS_ENDPOINT=https://book-mgmt-ots.cn-hangzhou.ots.aliyuncs.com
export OTS_TABLE_NAME=Books
export USERS_TABLE=Users
export VERIFICATION_CODES_TABLE=VerificationCodes
export BORROW_RECORDS_TABLE=BorrowRecords
export OSS_BUCKET_NAME=book-mgmt-images
export OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
export ALIYUN_ACCESS_KEY=your_access_key
export ALIYUN_ACCESS_SECRET=your_access_secret
export ALIYUN_REGION=cn-hangzhou
export EMAIL_HOST=smtp.qq.com
export EMAIL_PORT=465
export EMAIL_USER=your_email@qq.com
export EMAIL_PASSWORD=your_email_password
export FC_SERVER_PORT=9000
```

安装依赖并启动服务器

```bash
pip install flask tablestore oss2
python app.py
```

服务器将在 [http://localhost:9000](http://localhost:9000/) 启动

2.**启动前端客户端**：

配置环境变量（创建 `.env` 文件）：

```env
VITE_API_BASE=http://localhost:9000
VITE_OSS_BUCKET=book-mgmt-images
VITE_OSS_REGION=cn-hangzhou
```

安装依赖并启动客户端：

```python
npm install
npm run dev
```

前端应用将在 [http://localhost:3000](http://localhost:3000/) 启动





## 使用说明

### API接口文档

1.**获取API信息**

```text
GET /
```

响应示例

```json
{
  "message": "Backend is running"
}
```

2.**健康检查**

```text
GET /health
```

响应示例

```text
OK
```

3.**发送验证码**

```text
POST /send-verification-code
```

请求体:

```json
{
  "email": "user@example.com"
}
```

响应示例

```json
{
  "message": "Verification code sent"
}
```

4.**用户注册**

```text
POST /register
```

请求体:

```json
{
  "email": "user@example.com",
  "password": "password123",
  "code": "123456"
}
```

响应示例

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

5.**用户登陆**

```text
POST /login
```

请求体:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

响应示例

```json
{
  "token": "bearer-token-here",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@example.com",
  "role": "user"
}
```

6.**获取图书列表**

```text
GET /books?page=1&size=10&category=computer
```

**查询参数**

- page: 页码（默认1）
- size: 每页数量（默认10）
- category: 分类筛选（可选）

响应示例

```json
{
  "items": [
    {
      "book_id": "book-001",
      "title": "深入理解计算机系统",
      "cover": "https://example.com/cover.jpg",
      "category": "computer",
      "status": "available",
      "stock": 5,
      "author": "Randal E. Bryant",
      "publisher": "机械工业出版社",
      "price": 128.5
    }
  ],
  "total": 100,
  "page": 1,
  "size": 10
}
```

7.**获取单本图书信息**

```text
、GET /books/{book_id}
```

响应示例

```json
{
  "book_id": "book-001",
  "title": "深入理解计算机系统",
  "cover": "https://example.com/cover.jpg",
  "category": "computer",
  "status": "available",
  "stock": 5,
  "author": "Randal E. Bryant",
  "publisher": "机械工业出版社",
  "price": 128.5,
  "description": "本书从程序员的视角详细阐述计算机系统的本质概念...",
  "borrow_history": [
    {
      "borrow_id": "borrow-001",
      "user_id": "user-001",
      "borrow_date": 1634567890,
      "return_date": 1635172690,
      "status": "returned"
    }
  ]
}
```

8.**创建图书**

```text
POST /books
```

请求头:

```json
Authorization: Bearer <admin_token>
```

请求体:

```json
{
  "title": "新图书标题",
  "author": "作者名",
  "publisher": "出版社",
  "isbn": "9787115549441",
  "price": 68.5,
  "stock": 10,
  "category": "computer",
  "description": "图书描述内容",
  "cover": "https://example.com/cover.jpg"
}
```

响应示例

```json
{
  "book_id": "new-book-id",
  "message": "图书创建成功"
}
```

9.**更新图书信息**

```text
PUT /books/{book_id}
```

请求头:

```json
Authorization: Bearer <admin_token>
```

请求体:

```json
{
  "title": "更新后的标题",
  "stock": 8,
  "status": "available"
}
```

响应示例

```json
{
  "message": "Book updated successfully"
}
```

10.**删除图书**

```text
DELETE /books/{book_id}
```

请求头:

```json
Authorization: Bearer <admin_token>
```

响应示例

```json
{
  "message": "Book deleted successfully"
}
```

11.**获取OSS上传URL**

```text
GET /presigned-url?file_name=cover.jpg&file_type=image/jpeg
```

响应示例

```json
{
  "presigned_url": "https://bucket.oss-cn-hangzhou.aliyuncs.com/book-covers/uuid-cover.jpg?signature=...",
  "access_url": "https://bucket.oss-cn-hangzhou.aliyuncs.com/book-covers/uuid-cover.jpg"
}xxxxxxxxxx {  "presigned_url": "https://bucket.oss-cn-hangzhou.aliyuncs.com/book-covers/uuid-cover.jpg?signature=...",  "access_url": "https://bucket.oss-cn-hangzhou.aliyuncs.com/book-covers/uuid-cover.jpg"}{  "book_id": "new-book-id",  "message": "图书创建成功"}
```

12.**借阅图书**

```text
POST /books/{book_id}/borrow
```

请求头:

```json
Authorization: Bearer <user_token>
```

请求体:

```json
{
  "days": 30
}
```

响应示例

```json
{
  "success": true,
  "borrow_id": "borrow-12345",
  "due_date": 1635172690
}
```

13.**归还图书**

```text
POST /books/{book_id}/return
```

请求头:

```json
Authorization: Bearer <user_token>
```

响应示例

```json
{
  "success": true
}
```

14.**批量借阅图书**

```text
POST /books/batch-borrow
```

请求体:

```json
{
  "book_ids": ["book-001", "book-002", "book-003"]
}
```

响应示例

```json
{
  "success": true,
  "borrowed_count": 3,
  "results": [
    {
      "book_id": "book-001",
      "success": true,
      "borrow_id": "borrow-001",
      "due_date": 1635172690
    },
    {
      "book_id": "book-002",
      "success": true,
      "borrow_id": "borrow-002",
      "due_date": 1635172690
    },
    {
      "book_id": "book-003",
      "success": false,
      "error": "库存不足"
    }
  ]
}
```

15.**获取用户借阅记录**

```text
GET /user/borrows
```

请求头:

```json
Authorization: Bearer <user_token>
```

响应示例

```json
{
  "items": [
    {
      "borrow_id": "borrow-001",
      "book_id": "book-001",
      "user_id": "user-001",
      "book_title": "深入理解计算机系统",
      "book_cover": "https://example.com/cover.jpg",
      "borrow_date": 1634567890,
      "due_date": 1635172690,
      "return_date": 1635172690,
      "status": "returned"
    }
  ]
}
```

16.**批量归还图书**

```text
POST /batch-return
```

请求头:

```json
Authorization: Bearer <user_token>
```

请求体:

```json
{
  "borrow_ids": ["borrow-001", "borrow-002"]
}
```

响应示例

```json
{
  "success": true,
  "results": [
    {
      "borrow_id": "borrow-001",
      "success": true
    },
    {
      "borrow_id": "borrow-002",
      "success": false,
      "error": "记录已归还"
    }
  ]
}
```

17.**通过借阅ID归还图书**

```text
POST /return/{borrow_id}
```

请求头:

```json
Authorization: Bearer <user_token>
```

响应示例

```json
{
  "success": true
}
```



## 技术栈

- **前端**: Vue3 + Pinia + Element Plus + Vite
- **后端**: Flask + 阿里云OTS（表格存储） + OSS（对象存储）
- **部署**: 阿里云函数计算（FC）、Vercel
- **其他**: SMTP邮件服务（验证码）