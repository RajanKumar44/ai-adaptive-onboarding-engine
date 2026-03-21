import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../api/client'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    try {
      const savedToken = localStorage.getItem('access_token')
      const savedUser = localStorage.getItem('user')

      if (savedToken) {
        setToken(savedToken)
      }

      if (savedUser) {
        setUser(JSON.parse(savedUser))
      }
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      setUser(null)
      setToken(null)
    } finally {
      setLoading(false)
    }
  }, [])

  const register = async (emailOrPayload, nameArg, passwordArg, confirmPasswordArg) => {
    try {
      const isPayloadObject = typeof emailOrPayload === 'object' && emailOrPayload !== null
      const payload = isPayloadObject
        ? emailOrPayload
        : {
            email: emailOrPayload,
            name: nameArg,
            password: passwordArg,
            confirm_password: confirmPasswordArg,
          }

      const fullName = payload.name || [payload.first_name, payload.last_name].filter(Boolean).join(' ').trim()

      if (!payload.email || !payload.password || !payload.confirm_password || !fullName) {
        throw { detail: 'Please fill all required registration fields' }
      }

      const response = await authAPI.register({
        email: payload.email,
        name: fullName,
        password: payload.password,
        confirm_password: payload.confirm_password,
      })
      
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      
      // Fetch user profile
      const profile = await authAPI.getProfile()
      setUser(profile.data)
      localStorage.setItem('user', JSON.stringify(profile.data))
      setToken(response.data.access_token)
      
      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  }

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password })
      
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      
      // Fetch user profile
      const profile = await authAPI.getProfile()
      setUser(profile.data)
      localStorage.setItem('user', JSON.stringify(profile.data))
      setToken(response.data.access_token)
      
      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      setUser(null)
      setToken(null)
    }
  }

  const refreshProfile = async () => {
    try {
      const profile = await authAPI.getProfile()
      setUser(profile.data)
      localStorage.setItem('user', JSON.stringify(profile.data))
      return profile.data
    } catch (error) {
      throw error.response?.data || error
    }
  }

  const updateProfile = async (payload) => {
    try {
      const response = await authAPI.updateProfile(payload)
      setUser(response.data)
      localStorage.setItem('user', JSON.stringify(response.data))
      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  }

  const changePassword = async (payload) => {
    try {
      const response = await authAPI.changePassword(payload)
      return response.data
    } catch (error) {
      throw error.response?.data || error
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        register,
        login,
        logout,
        refreshProfile,
        updateProfile,
        changePassword,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
