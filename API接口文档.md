1. # FluxLib 图书管理系统接口文档

   本文档基于提供的前端（Frontend）和后端（Code）代码，梳理系统所有接口，按功能模块分类，包含接口名称、请求方式、URL、参数、响应及权限说明，确保前后端交互逻辑一致。

   ## 一、基础说明

   ### 1. 通用规则

   - **认证方式**：需登录的接口，请求头需携带 `Authorization: Bearer {token}`（`token` 为登录接口返回的用户 ID）。
   - **响应格式**：后端接口统一返回 `{ statusCode: 状态码, body: 响应内容 }`，`body` 为 JSON 字符串，前端需解析。
   - 状态码说明：
     - 200：请求成功
     - 400：参数错误
     - 401：未授权（未登录或 token 无效）
     - 403：权限不足（需管理员权限）
     - 404：资源不存在
     - 500：服务器错误

   ## 二、认证模块（Auth）

   处理用户登录、注册、密码重置等认证相关操作，无需登录即可访问。

   | 接口名称           | 请求方法 | 请求 URL                     | 请求参数                                                     | 响应数据（成功）                                             | 响应数据（失败）                           |
   | ------------------ | -------- | ---------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------ |
   | 发送注册验证码     | POST     | /send-verification-code      | Body: `{ email: string }`（用户注册邮箱）                    | `{ message: "验证码已发送至邮箱" }`                          | `{ error: "发送验证码失败" }`              |
   | 用户注册           | POST     | /register                    | Body: `{ email: string, password: string, code: string, gender?: string }`（code 为注册验证码） | `{ user_id: string }`（返回创建的用户 ID）                   | `{ error: "该邮箱已注册" / "验证码错误" }` |
   | 用户登录           | POST     | /login                       | Body: `{ email: string, password: string, admin_code?: string }`（admin_code 为管理员临时权限码） | `{ token: string, user_id: string, email: string, role: string, is_admin: boolean }` | `{ error: "用户不存在" / "密码错误" }`     |
   | 发送重置密码验证码 | POST     | /forgot-password/send-code   | Body: `{ email: string }`（已注册的邮箱）                    | `{ message: "验证码已发送至邮箱" }`                          | `{ error: "该邮箱未注册" }`                |
   | 验证重置密码验证码 | POST     | /forgot-password/verify-code | Body: `{ email: string, code: string }`                      | `{ success: true, message: "验证码验证成功" }`               | `{ error: "验证码错误/已过期" }`           |
   | 重置密码           | POST     | /forgot-password/reset       | Body: `{ email: string, code: string, new_password: string }` | `{ message: "密码重置成功" }`                                | `{ error: "验证码错误" }`                  |

   ## 三、图书模块（Book）

   处理图书的查询、创建、更新、删除及封面上传，部分接口需管理员权限。

   | 接口名称                | 请求方法 | 请求 URL         | 权限要求 | 请求参数                                                     | 响应数据（成功）                                             |
   | ----------------------- | -------- | ---------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
   | 获取图书列表            | GET      | /books           | 登录即可 | Query: `page?: number`（默认 1）、`size?: number`（默认 10）、`category?: string`（图书分类） | `{ items: Book[], total: number, page: number, size: number }`（Book 结构见下方备注） |
   | 获取图书详情            | GET      | /books/{book_id} | 登录即可 | Path: `book_id: string`（图书 ID）                           | `{ book_id: string, title: string, author: string, ... }`（完整图书信息，含借阅历史） |
   | 创建图书                | POST     | /books           | 管理员   | Body: `BookCreateData`（见备注）                             | `{ book_id: string, message: "图书创建成功" }`               |
   | 更新图书                | PUT      | /books/{book_id} | 管理员   | Path: `book_id: string`；Body: `BookUpdateData`（见备注）    | `{ message: "Book updated successfully" }`                   |
   | 删除图书                | DELETE   | /books/{book_id} | 管理员   | Path: `book_id: string`                                      | `{ message: "Book deleted successfully" }`                   |
   | 获取 OSS 上传预签名 URL | GET      | /presigned-url   | 登录即可 | Query: `file_name: string`（文件名）、`file_type: string`（文件 MIME 类型，如 image/jpeg） | `{ presigned_url: string, access_url: string }`（presigned_url 用于上传，access_url 为最终访问地址） |

   ### 备注：Book 相关数据结构

   - Book（图书完整信息）：

     ```json
     {
       "book_id": "string", "title": "string", "author": "string", "publisher": "string",
       "isbn": "string", "price": number, "category": "string", "description": "string",
       "cover": "string", "summary": "string", "status": "available/borrowed/maintenance",
       "stock": number, "created_at": number, "updated_at": number, "borrow_history": BorrowRecord[]
     }
     ```

   - BookCreateData（创建图书参数）：

     ```json
     {
       "title": "string", "author": "string", "publisher": "string", "isbn": "string",
       "price": number, "stock": number, "category": "string", "description": "string",
       "cover": "string", "summary": "string", "status": "available"
     }
     ```

   - **BookUpdateData**（更新图书参数）：与 BookCreateData 一致，字段可选（仅传需更新的字段）。

   ## 四、借阅模块（Borrow）

   处理图书借阅、归还、批量操作及借阅记录查询，需登录访问。

   | 接口名称         | 请求方法 | 请求 URL                      | 权限要求 | 请求参数                                                     | 响应数据（成功）                                             |
   | ---------------- | -------- | ----------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
   | 借阅图书         | POST     | /books/{book_id}/borrow       | 登录即可 | Path: `book_id: string`；Body: `{ days?: number }`（借阅天数，默认 30） | `{ success: true, borrow_id: string, message: "借阅成功" }`  |
   | 按期归还图书     | POST     | /books/{book_id}/return       | 登录即可 | Path: `book_id: string`                                      | `{ success: true, message: "归还成功" }`                     |
   | 提前归还图书     | POST     | /books/{book_id}/return-early | 登录即可 | Path: `book_id: string`                                      | `{ success: true, message: "提前归还成功" }`                 |
   | 批量归还图书     | POST     | /batch-return                 | 登录即可 | Body: `{ borrow_ids: string[] }`（需归还的借阅 ID 列表）     | `{ success: true, returned_count: number }`（returned_count 为成功归还数量） |
   | 通过借阅 ID 归还 | POST     | /return/{borrow_id}           | 登录即可 | Path: `borrow_id: string`（借阅记录 ID）                     | `{ success: true, message: "归还成功" }`                     |
   | 获取用户借阅记录 | GET      | /user/borrows                 | 登录即可 | -                                                            | `{ items: BorrowRecord[], total: number }`（BorrowRecord 见备注） |
   | 获取所有借阅记录 | GET      | /borrows                      | 管理员   | -                                                            | `{ items: BorrowRecord[], total: number }`                   |

   ### 备注：BorrowRecord（借阅记录）

   ```json
   {
     "borrow_id": "string", "book_id": "string", "user_id": "string",
     "borrow_date": number, "due_date": number, "return_date": number,
     "status": "borrowed/returned", "is_early_return": boolean
   }
   ```

   ## 五、用户模块（User）

   处理用户信息查询、更新及个性化操作，需登录访问。

   | 接口名称         | 请求方法 | 请求 URL                 | 权限要求 | 请求参数                                                     | 响应数据（成功）                                             |
   | ---------------- | -------- | ------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
   | 获取当前用户信息 | GET      | /user/current            | 登录即可 | -                                                            | `{ user_id: string, email: string, display_name: string, avatar_url: string, ... }`（完整用户信息） |
   | 更新用户资料     | PUT      | /user/profile            | 登录即可 | Body/FormData: `UserProfileData`（见备注，支持表单上传头像 / 背景图） | `{ user: User }`（更新后的用户信息）                         |
   | 预约图书         | POST     | /books/{book_id}/reserve | 登录即可 | Path: `book_id: string`；Body: `{ reserve_date: string, time_slot: string, days?: number }`（预约日期、时间段、借阅天数） | `{ success: true, reservation_id: string }`                  |

   ### 备注：UserProfileData（用户资料更新参数）

   - 普通文本更新（JSON 格式）：

     ```json
     {
       "display_name": "string", "gender": "male/female/other",
       "summary": "string", "avatar_url": "string", "background_url": "string"
     }
     ```

     

   - 图片上传（FormData 格式）：

     - 字段：`avatar: File`（头像文件）、`background: File`（背景图文件），可搭配文本字段一起传。

   ## 六、收藏与浏览历史模块（Favorite & History）

   处理用户图书收藏和浏览历史记录，需登录访问。

   | 接口名称         | 请求方法 | 请求 URL                   | 权限要求 | 请求参数                | 响应数据（成功）                                             |
   | ---------------- | -------- | -------------------------- | -------- | ----------------------- | ------------------------------------------------------------ |
   | 添加图书收藏     | POST     | /favorites/{book_id}       | 登录即可 | Path: `book_id: string` | `{ success: true }`                                          |
   | 取消图书收藏     | DELETE   | /favorites/{book_id}       | 登录即可 | Path: `book_id: string` | `{ success: true }`                                          |
   | 检查图书收藏状态 | GET      | /favorites/{book_id}/check | 登录即可 | Path: `book_id: string` | `{ is_favorited: boolean }`（true = 已收藏，false = 未收藏） |
   | 获取用户收藏列表 | GET      | /favorites                 | 登录即可 | -                       | `{ items: FavoriteItem[], total: number }`（FavoriteItem 见备注） |
   | 获取用户浏览历史 | GET      | /history                   | 登录即可 | -                       | `{ items: HistoryItem[], total: number }`（HistoryItem 见备注） |

   ### 备注：数据结构

   - FavoriteItem（收藏项）：

     ```json
     {
       "favorite_id": "string", "user_id": "string", "book_id": "string",
       "book_title": "string", "book_cover": "string", "book_author": "string", "created_at": number
     }
     ```

     

   - HistoryItem（浏览历史项）：

     ```json
     {
       "history_id": "string", "user_id": "string", "book_id": "string",
       "book_title": "string", "book_cover": "string", "view_time": number
     }
     ```

     

   ## 七、评论模块（Comment）

   处理图书评论的查询、创建及点赞，需登录访问。

   | 接口名称            | 请求方法 | 请求 URL                    | 权限要求 | 请求参数                                                     | 响应数据（成功）                                             |
   | ------------------- | -------- | --------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
   | 获取图书评论列表    | GET      | /books/{book_id}/comments   | 登录即可 | Path: `book_id: string`                                      | `{ items: Comment[], total: number }`（Comment 见备注，含嵌套回复） |
   | 创建评论 / 回复     | POST     | /books/{book_id}/comments   | 登录即可 | Path: `book_id: string`；Body: `{ content: string, parent_id?: string }`（parent_id 为父评论 ID，回复时必传） | `{ success: true, comment: Comment }`（创建的评论信息）      |
   | 评论点赞 / 取消点赞 | POST     | /comments/{comment_id}/like | 登录即可 | Path: `comment_id: string`                                   | `{ success: true, likes: number, action: "点赞/取消点赞" }`  |

   ### 备注：Comment（评论）

   ```json
   {
     "comment_id": "string", "book_id": "string", "user_id": "string",
     "user_display_name": "string", "user_avatar_url": "string",
     "content": "string", "parent_id": "string", "likes": number,
     "created_at": number, "replies": Comment[]（嵌套回复列表）
   }
   ```

   ## 八、AI 聊天模块（AI）

   处理用户与 AI 助手的交互，基于图书数据提供响应，需登录访问。

   | 接口名称    | 请求方法 | 请求 URL | 权限要求 | 请求参数                                    | 响应数据（成功）                                             |
   | ----------- | -------- | -------- | -------- | ------------------------------------------- | ------------------------------------------------------------ |
   | AI 聊天交互 | POST     | /ai/chat | 登录即可 | Body: `{ message: string }`（用户提问内容） | `{ response: string, timestamp: number }`（response 为 AI 回复，timestamp 为时间戳） |

   ## 九、公告模块（Announcement）

   处理系统公告的查询、创建及删除，创建 / 删除需管理员权限。

   | 接口名称     | 请求方法 | 请求 URL                         | 权限要求 | 请求参数                                                     | 响应数据（成功）                                             |
   | ------------ | -------- | -------------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
   | 获取公告列表 | GET      | /announcements                   | 登录即可 | -                                                            | `{ items: Announcement[], total: number }`（Announcement 见备注） |
   | 创建公告     | POST     | /announcements                   | 管理员   | Body: `{ title: string, content: string }`（公告标题、内容） | `{ success: true }`                                          |
   | 删除公告     | DELETE   | /announcements/{announcement_id} | 管理员   | Path: `announcement_id: string`（公告 ID）                   | `{ success: true }`                                          |

   ### 备注：Announcement（公告）

   ```json
   {
     "announcement_id": "string", "title": "string", "content": "string",
     "publish_time": number, "created_at": number
   }
   ```

   ## 十、权限说明汇总

   | 权限类型     | 可访问接口范围                                               |
   | ------------ | ------------------------------------------------------------ |
   | 未登录用户   | 认证模块所有接口（登录、注册、密码重置）                     |
   | 普通登录用户 | 图书查询、借阅 / 归还、用户信息查询 / 更新、收藏 / 浏览历史、评论、AI 聊天、公告查询 |
   | 管理员用户   | 普通用户所有权限 + 图书创建 / 更新 / 删除、所有借阅记录查询、公告创建 / 删除 |