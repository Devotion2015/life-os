// Life OS 认证配置
// 修改 AUTH_KEY 为自己的密码后重新 npm run build 部署

export const AUTH_KEY = '20260505'

// SHA-256 哈希（浏览器 Web Crypto API）
export async function hashKey(key) {
  const encoder = new TextEncoder()
  const data = encoder.encode(key)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}
