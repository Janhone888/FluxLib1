import axios from 'axios';
import { useUserStore } from '@/stores/user';

const API_BASE = import.meta.env.VITE_API_BASE;

// 创建 axios 实例
const apiInstance = axios.create();

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

const api = {
  // 用户认证API
  sendVerificationCode: (email) =>
    apiInstance.post(`${API_BASE}/send-verification-code`, { email }).then(handleResponse),

  register: (data) =>
    apiInstance.post(`${API_BASE}/register`, data).then(handleResponse),

  login: (credentials) =>
    apiInstance.post(`${API_BASE}/login`, credentials).then(handleResponse),

  // 图书相关API
  getBooks: (page = 1, size = 10, category = '') => {
    let url = `${API_BASE}/books?page=${page}&size=${size}`;
    if (category) {
      url += `&category=${category}`;
    }
    return apiInstance.get(url).then(handleResponse);
  },

  getBook: (id) =>
    apiInstance.get(`${API_BASE}/books/${id}`).then(handleResponse),

  createBook: (bookData) =>
    apiInstance.post(`${API_BASE}/books`, bookData).then(handleResponse),

  updateBook: (id, bookData) =>
    apiInstance.put(`${API_BASE}/books/${id}`, bookData).then(handleResponse),

  deleteBook: (id) =>
    apiInstance.delete(`${API_BASE}/books/${id}`).then(handleResponse),

  // 图书借阅/归还API
  borrowBook: (bookId, days) =>
    apiInstance.post(`${API_BASE}/books/${bookId}/borrow`, { days }).then(handleResponse),

  returnBook: (bookId) =>
    apiInstance.post(`${API_BASE}/books/${bookId}/return`).then(handleResponse),

  // 上传相关API
  getUploadUrl: (fileName, fileType) =>
    apiInstance.get(`${API_BASE}/presigned-url?file_name=${fileName}&file_type=${fileType}`).then(handleResponse),

  // 借阅记录API
  getUserBorrows: () =>
    apiInstance.get(`${API_BASE}/user/borrows`).then(handleResponse),

  // 批量归还API
  batchReturnBooks: (data) =>
    apiInstance.post(`${API_BASE}/batch-return`, data).then(handleResponse),

  // 通过借阅ID归还API
  returnBookByBorrowId: (borrowId) =>
    apiInstance.post(`${API_BASE}/return/${borrowId}`).then(handleResponse),
};

export default api;