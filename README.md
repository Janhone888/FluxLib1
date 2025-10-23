## FluxLib泛集库

![image](https://github.com/Janhone888/FluxLib1/blob/main/picture/5e092c69a875d7eda7038c4524285506.png)

![image](https://github.com/Janhone888/FluxLib1/blob/main/picture/f2fc046b71aed54fc2f4ecb0ab142188.png)

FluxLib 智能图书管理系统是一套基于**前后端分离架构**的现代化图书馆管理解决方案，整合了图书全生命周期管理、用户权限控制、借阅预约流程、互动社区及 AI 智能助手功能。系统解决传统图书馆 “管理效率低、用户操作繁琐、信息同步不及时、服务智能化不足” 等痛点，为管理员提供高效的后台管理与数据可视化工具，为普通用户提供 “查询 - 借阅 - 互动 - 反馈” 的一站式图书服务体验，同时支持多端适配与云端部署。

由于前端部署在Vercel，后端部署在阿里云函数计算，需要使用外网点击[https://book-mgmt-2y6iok4zv-janhones-projects.vercel.app]，打开我们的网站。打不开可能我正在维护中或者我欠费了，来不及续费。

蓝湖地址：https://lanhuapp.com/link/#/invite?sid=qXdn4qCa
分享人: 微信用户Ws4G
团队名称: 微信用户IOX6的团队的团队
相关项目: FluxLib泛集库

## 关键特性（Features）

### 1 .核心业务功能

- **用户管理模块**：支持用户注册（邮箱验证码）、登录（普通用户 / 管理员权限区分）、密码重置、个人资料编辑（头像 / 背景图上传）、角色控制（admin/user）。
- **图书管理模块**：管理员可实现图书 CRUD（含封面 OSS 上传）、分类管理、库存控制；用户可按分类 / 关键词查询图书、查看详情及借阅历史。
- **借阅预约模块**：支持单本 / 批量借阅、按期 / 提前归还、图书预约（指定日期 / 时间段）、借阅记录查询，自动同步图书库存状态。
- **互动社区模块**：用户可对图书发表评论、回复评论、点赞评论，支持收藏图书、查看浏览历史，形成用户与图书的互动闭环。
- **AI 智能助手模块**：基于 DeepSeek 大模型，整合系统内图书数据，为用户提供图书推荐、借阅规则解答、图书馆营业时间查询等智能服务，支持拖拽 / 缩放聊天窗口。

### 2 技术特性

- **架构设计**：采用 “仓储模式（Repository Pattern）” 解耦数据访问与业务逻辑，后端分层清晰（模型 - 仓储 - 服务 - 路由），前端基于 Vue3+Pinia 实现状态管理。
- **云端集成**：依赖阿里云 OTS（表格存储）存储业务数据、OSS 存储图书封面 / 用户头像，确保数据高可用；Redis 缓存用户 Token 与高频数据，提升性能。
- **安全优化**：密码 SHA256 哈希存储、Token 身份验证、管理员操作权限校验、验证码有效期控制，保障系统安全。
- **数据可视化**：管理员端提供借阅趋势折线图、图书分类饼图、热门图书柱状图，支持数据驱动决策。



## 快速开始（Quick Start）

本指南帮助你 5 分钟内本地运行系统或部署到云端，体验核心功能。

### 1. 后端（阿里云部署 / 本地运行）

#### 本地运行步骤

1. **克隆代码**

   ```bash
   git clone https://github.com/your-username/fluxlib-backend.git
   cd fluxlib-backend/Code
   ```

2. **配置环境变量**创建`.env`文件，填入以下配置（需提前准备阿里云 OTS/OSS 账号、Redis 地址）：

   ```env
   # 阿里云密钥
   ALIYUN_ACCESS_KEY=your-aliyun-access-key
   ALIYUN_ACCESS_SECRET=your-aliyun-access-secret
   # OTS配置
   OTS_INSTANCE_NAME=book-mgmt-ots
   OTS_ENDPOINT=https://book-mgmt-ots.cn-hangzhou.ots.aliyuncs.com
   # OSS配置
   OSS_BUCKET_NAME=book-mgmt-images
   OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
   # Redis配置
   REDIS_HOST=your-redis-host
   REDIS_PORT=6379
   REDIS_PASSWORD=your-redis-password
   # AI配置
   DEEPSEEK_API_KEY=your-deepseek-api-key
   # 管理员配置
   ADMIN_CODE=10N086
   ADMIN_EMAIL=admin@bookmgmt.com
   ADMIN_DEFAULT_PASSWORD=Admin@1234
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt  # 依赖含Flask、aliyun-ots-sdk、redis、requests等
   ```

4. **启动服务**

   ```bash
   python main.py  # 服务默认运行在9000端口
   ```

### 2.前端（Vercel 部署 / 本地运行）

#### 本地运行步骤

1. **克隆代码**

   ```bash
   git clone https://github.com/your-username/fluxlib-frontend.git
   cd fluxlib-frontend/Frontend
   ```

2. **配置后端 API 地址**修改`Frontend/.env.development`：

   ```env
   VITE_API_BASE=http://localhost:9000  # 本地后端地址；部署时改为阿里云后端域名
   ```

3. **安装依赖**

   ```bash
   npm install  # 依赖含Vue3、Element-Plus、Pinia、ECharts等
   ```

4. **本地启动**

   ```bash
   npm run dev  # 前端默认运行在5173端口
   ```

#### 部署到 Vercel

1. 访问[Vercel 官网](https://vercel.com/)，登录后点击 “New Project”；
2. 选择 “Import Git Repository”，粘贴前端仓库地址；
3. 配置环境变量`VITE_API_BASE`（填入阿里云后端公网域名）；
4. 点击 “Deploy”，等待部署完成，获取前端访问地址。



##  环境要求（Prerequisites）

| 环境 / 工具      | 版本要求            | 用途说明                             |
| ---------------- | ------------------- | ------------------------------------ |
| Python           | 3.8+                | 后端运行环境                         |
| Node.js          | 16+                 | 前端 Vue3 项目构建与运行             |
| Redis            | 6.0+                | 用户 Token 缓存、高频数据缓存        |
| 阿里云服务       | OTS/OSS 开通        | 数据存储（OTS）、静态资源存储（OSS） |
| DeepSeek API Key | 有效密钥            | AI 智能助手功能（可选，无则屏蔽 AI） |
| 浏览器           | Chrome 90+/Edge 90+ | 前端页面访问                         |



## 安装步骤（Installation）

### 1. 后端安装

```bash
git clone https://github.com/your-username/fluxlib-backend.git
cd fluxlib-backend
```

1. **虚拟环境配置（推荐）**

   ```bash
   # 创建虚拟环境
   python -m venv venv
   # 激活虚拟环境（Windows）
   venv\Scripts\activate
   # 激活虚拟环境（Linux/Mac）
   source venv/bin/activate
   ```

2. **依赖安装**项目根目录创建`requirements.txt`（根据代码依赖补充）：

   ```txt
   Flask==2.3.3
   flask-cors==4.0.0
   aliyun-ots-sdk==5.11.0
   redis==4.6.0
   requests==2.31.0
   python-dotenv==1.0.0
   cryptography==2.9.2
   pycryptodomex==3.9.9
   ```

   执行安装：

   ```bash
   pip install -r requirements.txt
   ```

3. **环境变量配置**根目录创建`.env`文件，配置内容参考 “4.1 后端快速开始” 中的环境变量说明。

### 2. 前端安装

1. **代码克隆**

   ```bash
   git clone https://github.com/your-username/fluxlib-frontend.git
   cd fluxlib-frontend/Frontend
   ```

2. **依赖安装**

   ```bash
   npm install  # 自动安装package.json中的依赖（Vue3、Element-Plus等）
   ```

3. **环境配置**根据运行环境创建对应`.env`文件（如`.env.development`本地开发、`.env.production`生产环境），核心配置为`VITE_API_BASE`（后端 API 地址）。



## 运行命令（Run）

### 1. 本地运行

| 模块 | 命令             | 说明                            |
| ---- | ---------------- | ------------------------------- |
| 后端 | `python main.py` | 启动后端服务，默认端口 9000     |
| 前端 | `npm run dev`    | 启动前端开发服务，默认端口 5173 |

### 2. 部署命令

#### 后端（阿里云）

1. 打包依赖

   ```bash
   pip freeze > requirements.txt  # 导出实际依赖
   ```

2. 部署方式

   - 方式 1：直接部署到阿里云 ECS，通过`nohup python main.py &`后台运行；
   - 方式 2：构建 Docker 镜像（需创建 Dockerfile），通过容器部署。

#### 前端（Vercel）

1. 无需本地打包，直接在 Vercel 控制台 “Import Project”，选择前端 Git 仓库；
2. 配置环境变量`VITE_API_BASE`，点击 “Deploy” 自动部署。



## 使用指南（Usage）

### 1. 核心功能演示（用户视角）

#### 1). 用户登录

- 访问前端地址（本地：[http://localhost:5173](http://localhost:5173/)，Vercel：部署后的域名）；
- 点击 “登录”，选择 “使用演示账号”（或手动输入：邮箱`2292974063@qq.com`，密码`123456`）；
- 登录后自动跳转至用户首页。

#### 2). 图书查询与借阅

- 在首页点击 “图书浏览”，进入图书列表页；
- 可通过顶部搜索框输入关键词（如 “Python”）查询图书，或通过下拉框筛选分类（如 “计算机”）；
- 点击图书卡片进入详情页，查看图书信息（封面、作者、简介等）；
- 若图书有库存，点击 “预约借阅”，选择预约日期和时间段，提交完成预约。

#### 3). AI 智能助手互动

- 点击页面右下角 “AI 助手” 图标，展开聊天窗口；
- 在输入框发送问题，例如：“推荐 3 本计算机类的图书”“图书馆的营业时间是什么？”；
- 等待 AI 响应（基于系统内图书数据生成推荐，遵循借阅规则）。

#### 4). 个人中心操作

- 点击顶部导航 “个人中心”，可编辑头像、昵称、个人简介；
- 查看 “我的借阅”（已借阅 / 已归还记录）、“我的收藏”（取消收藏）、“浏览历史”。

### 2. 管理员功能演示

- 使用管理员账号登录（默认：邮箱`admin@bookmgmt.com`，密码`Admin@1234`）；
- 登录后跳转至 “仪表盘”，查看图书总数、借阅趋势、分类分布等数据；
- 点击 “图书管理”，可执行图书添加（上传封面至 OSS）、编辑、删除操作；
- 点击 “借阅管理”，可查看所有用户的借阅记录，支持批量归还操作。



##  项目结构（Project Structure）

### 1. 后端结构（Code/）

```plaintext
Code/
├── models/                # 数据模型层（基于仓储模式）
│   ├── book.py            # 图书模型（属性、CRUD方法）
│   ├── user.py            # 用户模型（注册、登录、权限）
│   ├── borrow.py          # 借阅模型（借阅、归还逻辑）
│   └── ...（announcement/comment/reservation等模型）
├── repositories/          # 仓储层（数据访问抽象，解耦模型与数据库）
│   ├── base_repository.py# 仓储基类（定义通用接口：get_by_id、create等）
│   ├── book_repository.py# 图书仓储（OTS数据读写）
│   └── ...（对应模型的仓储实现）
├── routes/                # 路由层（API接口定义）
│   ├── book_routes.py     # 图书相关接口（/books、/books/<id>）
│   ├── auth_routes.py     # 认证接口（/login、/register）
│   └── ...（其他业务路由）
├── services/              # 业务逻辑层（整合模型与仓储，处理业务规则）
│   ├── book_service.py    # 图书业务（获取列表、更新库存）
│   ├── ai_service.py      # AI服务（DeepSeek调用、图书数据组装）
│   └── ...（对应业务的服务实现）
├── utils/                 # 工具类
│   ├── auth.py           # 认证工具（密码哈希、Token验证、Redis缓存）
│   ├── database.py        # 数据库工具（OTS客户端、表格创建）
│   ├── email.py          # 邮件工具（验证码发送）
│   └── storage.py         # OSS工具（预签名URL生成、文件上传）
├── config.py              # 全局配置（环境变量读取、日志配置）
└── main.py                # 应用入口（Flask初始化、路由注册、服务启动）
```

### 2. 前端结构（Frontend/src/）

```plaintext
Frontend/src/
├── components/            # 通用组件
│   ├── BookCard.vue       # 图书卡片（列表页展示）
│   ├── ChatBot.vue        # AI助手（可拖拽、缩放、最小化）
│   ├── ImageUploader.vue  # 图片上传（封面/头像，对接OSS）
│   └── ...（TopNav/SearchBar等组件）
├── views/                 # 页面组件
│   ├── LoginView.vue      # 登录/注册页面
│   ├── BooksView.vue      # 图书列表页面
│   ├── BookDetail.vue     # 图书详情页面
│   ├── Dashboard.vue      # 管理员仪表盘
│   └── ...（个人中心、借阅管理等页面）
├── stores/                # Pinia状态管理
│   ├── user.py            # 用户状态（Token、用户信息）
│   ├── book.py            # 图书状态（列表、详情、借阅状态）
│   └── ...（其他业务状态）
├── router/                # 路由配置
│   └── index.js          # 路由定义、权限守卫（管理员路由拦截）
├── utils/                 # 工具类
│   └── api.js             # Axios封装（请求拦截、响应处理、API集合）
├── assets/                # 静态资源
│   ├── styles/            # 样式文件（变量、动画）
│   └── icons/             # 图标资源
└── App.vue                # 根组件（布局、导航）
```



## 技术栈总结

| 层面     | 技术选型            | 核心作用                               |
| -------- | ------------------- | -------------------------------------- |
| 后端语言 | Python 3.8+         | 业务逻辑实现                           |
| 后端框架 | Flask               | 轻量级 Web 框架，路由与中间件管理      |
| 数据库   | 阿里云 OTS          | 分布式表格存储（支持高并发、海量数据） |
| 静态存储 | 阿里云 OSS          | 图书封面、用户头像存储                 |
| 缓存     | Redis               | Token 缓存、高频数据加速               |
| 前端框架 | Vue 3 + Pinia       | 组件化开发、状态管理                   |
| 前端 UI  | Element-Plus        | 通用组件（表格、表单、弹窗）           |
| 可视化   | ECharts             | 管理员仪表盘数据可视化                 |
| AI 能力  | DeepSeek API        | 智能问答与图书推荐                     |
| 部署     | 阿里云 ECS + Vercel | 后端云端部署、前端静态部署             |