import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // 确保Element Plus路径正确
      'element-plus': 'element-plus',
      'element-plus/es': 'element-plus/es'
    }
  },
  // 生产环境配置
  build: {
    // 代码分割配置（优化大文件问题）
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 将大依赖包拆分
          if (id.includes('node_modules')) {
            const module = id.split('node_modules/')[1].split('/')[0];

            // 单独打包Element Plus
            if (module === 'element-plus') {
              return 'element-plus';
            }

            // 单独打包Echarts
            if (module === 'echarts') {
              return 'echarts';
            }

            // 其他依赖打包到vendor
            return 'vendor';
          }
        }
      }
    },
    // 调整块大小警告限制
    chunkSizeWarningLimit: 1500, // 1.5MB
    // 生产环境移除console和debugger
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  // 开发服务器配置
  server: {
    port: 5173,
    proxy: {
      // 开发环境API代理
      '/api': {
        target: 'https://book-mgmt-cn-hangzhou.1942651803045592.fcapp.run',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  // 环境变量配置
  define: {
    // 解决process.env未定义问题
    'process.env': {}
  },
  css: {
    preprocessorOptions: {
      scss: {
        // 全局注入scss变量
        additionalData: `@import "@/assets/styles/variables.scss";`
      }
    }
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'element-plus',
      'axios',
      'echarts'
    ],
    exclude: ['vue-demi']
  }
});