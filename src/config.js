// Life OS 认证配置
// ⚠️ 只存 SHA-256 哈希值，不是明文密码！
// 修改密码：node -e "const c=require('crypto');console.log(c.createHash('sha256').update('新密码').digest('hex'))"
// 把得到的哈希替换下面这行，重新 npm run build 部署

export const AUTH_HASH = '2e40a5bdc2a8dd0ebc76d10af7f6bb856dd06acbb45673ea4267fbebe74c01f4'

// SHA-256 哈希（浏览器 Web Crypto API）
export async function hashKey(key) {
  const encoder = new TextEncoder()
  const data = encoder.encode(key)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}
