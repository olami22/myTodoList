import { useCallback, useEffect, useState } from 'react'

import { api } from '../../api/client'

export function useAuth() {
  const [currentUser, setCurrentUser] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isActive = true

    api.get('/me')
      .then(({ data }) => {
        if (isActive) {
          setCurrentUser(data.username)
          setIsAuthenticated(true)
        }
      })
      .catch(() => {
        if (isActive) {
          setCurrentUser('')
          setIsAuthenticated(false)
        }
      })
      .finally(() => {
        if (isActive) setIsLoading(false)
      })

    return () => {
      isActive = false
    }
  }, [])

  const login = useCallback(async (username, password) => {
    const { data } = await api.post('/login', { username, password })

    setCurrentUser(data.username)
    setIsAuthenticated(true)

    return data
  }, [])

  const register = useCallback(async (username, password) => {
    await api.post('/register', { username, password })
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.post('/logout')
    } finally {
      setCurrentUser('')
      setIsAuthenticated(false)
    }
  }, [])

  return {
    currentUser,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
  }
}
