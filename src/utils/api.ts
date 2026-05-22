import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import type { ApiResponse } from '@/types'

const instance: AxiosInstance = axios.create({
  baseURL: '/api/',
  timeout: 10000,
  headers: {
    'X-Requested-With': 'XMLHttpRequest'
  },
  withCredentials: true
})

instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

instance.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => response,
  (error: AxiosError) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default instance
