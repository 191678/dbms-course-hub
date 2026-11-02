export interface AuthUser {
  id: number
  student_id: string
  username: string
  name: string
  role: string
}

export interface AuthTokens {
  access_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}

const TOKEN_KEY = 'dbms_access_token'
const USER_KEY = 'dbms_user_info'
const EXPIRES_KEY = 'dbms_token_expires'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string, expiresIn: number): void {
  localStorage.setItem(TOKEN_KEY, token)
  const expiryTime = Date.now() + (expiresIn * 1000)
  localStorage.setItem(EXPIRES_KEY, String(expiryTime))
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(EXPIRES_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getUser(): AuthUser | null {
  const userStr = localStorage.getItem(USER_KEY)
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }
  return null
}

export function setUser(user: AuthUser): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function setAuthData(data: AuthTokens): void {
  setToken(data.access_token, data.expires_in)
  setUser(data.user)
}

export function isAuthenticated(): boolean {
  const token = getToken()
  const expiresStr = localStorage.getItem(EXPIRES_KEY)
  if (!token || !expiresStr) {
    return false
  }
  const expiresTime = Number(expiresStr)
  return Date.now() < expiresTime
}

export function logout(): void {
  clearToken()
}

export function getAuthHeader(): Record<string, string> {
  const token = getToken()
  if (token) {
    return { Authorization: `Bearer ${token}` }
  }
  return {}
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (minutes < 60) return `${minutes}分${remainingSeconds}秒`
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return `${hours}时${remainingMinutes}分`
}
