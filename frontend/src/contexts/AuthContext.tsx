import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../api/axios'

interface User {
  id: number
  email: string
  username: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  const { data: userData, isLoading } = useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      try {
        const response = await api.get('/auth/me')
        return response.data
      } catch (error) {
        return null
      }
    },
    enabled: !!localStorage.getItem('token')
  })

  useEffect(() => {
    if (userData) {
      setUser(userData)
    }
  }, [userData])

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 