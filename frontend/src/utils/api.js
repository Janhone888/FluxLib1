import axios from 'axios';
import { useUserStore } from '@/stores/user';
import { ElMessage } from 'element-plus';

const API_BASE = import.meta.env.VITE_API_BASE;

// 创建 axios 实例
const apiInstance = axios.create({
  baseURL: API_BASE,
  timeout: 30000, // 30秒超时
});

// 请求拦截器 - 添加认证头
apiInstance.interceptors.request.use(config => {
  const userStore = useUserStore();
  if (userStore.isAuthenticated && userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// 响应拦截器 - 统一错误处理
apiInstance.interceptors.response.use(
  response => {
    return handleResponse(response);
  },
  error => {
    if (error.response) {
      // 服务器返回错误状态码
      const status = error.response.status;
      const message = error.response.data?.error || '请求失败';

      if (status === 401) {
        // 未授权，清除用户信息并跳转到登录页
        const userStore = useUserStore();
        userStore.logout();
        ElMessage.warning('登录已过期，请重新登录');
        window.location.href = '/login';
      } else if (status === 403) {
        ElMessage.warning('权限不足');
      } else if (status >= 500) {
        ElMessage.error('服务器错误，请稍后再试');
      } else {
        ElMessage.error(message);
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error('网络错误，请检查网络连接');
    } else {
      // 其他错误
      ElMessage.error('请求配置错误');
    }

    return Promise.reject(error);
  }
);

// 统一处理所有API响应
const handleResponse = (response) => {
  // 统一处理函数计算返回的嵌套结构
  if (response.data && response.data.body) {
    try {
      return {
        ...response,
        data: JSON.parse(response.data.body)
      };
    } catch (e) {
      console.error('JSON解析错误:', e);
      return response;
    }
  }
  return response;
};

// API函数集合
const api = {
  // 用户认证API
  sendVerificationCode: (email) =>
    apiInstance.post('/send-verification-code', { email }),

  register: (data) =>
    apiInstance.post('/register', data),

  login: (credentials) =>
    apiInstance.post('/login', credentials),

  // 图书相关API
  getBooks: (page = 1, size = 10, category = '') => {
    let url = `/books?page=${page}&size=${size}`;
    if (category) {
      url += `&category=${category}`;
    }
    return apiInstance.get(url);
  },

  getBook: (id) =>
    apiInstance.get(`/books/${id}`),

  createBook: (bookData) =>
    apiInstance.post('/books', bookData),

  updateBook: (id, bookData) =>
    apiInstance.put(`/books/${id}`, bookData),

  deleteBook: (id) =>
    apiInstance.delete(`/books/${id}`),

  // 图书借阅/归还API
  borrowBook: (bookId, days = 30) =>
    apiInstance.post(`/books/${bookId}/borrow`, { days }),

  returnBook: (bookId) =>
    apiInstance.post(`/books/${bookId}/return`),

  // 上传相关API
  getUploadUrl: (fileName, fileType) =>
    apiInstance.get(`/presigned-url?file_name=${fileName}&file_type=${fileType}`),

  // 借阅记录API
  getUserBorrows: () =>
    apiInstance.get('/user/borrows'),

  // 批量归还API
  batchReturnBooks: (data) =>
    apiInstance.post('/batch-return', data),

  // 通过借阅ID归还API
  returnBookByBorrowId: (borrowId) =>
    apiInstance.post(`/return/${borrowId}`),

  // AI聊天API - 新增
  sendAIMessage: (message) =>
    apiInstance.post('/ai/chat', { message }),
};

export default api;