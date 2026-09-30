import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function getLoginErrorMessage(requestError) {
  if (!requestError.response) {
    return 'Cannot reach the authentication service. Please try again.'
  }

  if (requestError.response.status >= 500) {
    return `Authentication service unavailable (HTTP ${requestError.response.status}). Please try again later.`
  }

  return requestError.response.data?.detail || 'Invalid username or password.'
}

function LoginPage({ onLogin }) {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await onLogin(username, password)
      navigate('/')
    } catch (requestError) {
      setError(getLoginErrorMessage(requestError))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <h2>Login</h2>
      <form className="auth-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
        {error && <p className="auth-error">{error}</p>}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in...' : 'Login'}
        </button>
      </form>
      <p className="auth-switch">
        Need an account? <Link to="/register">Register</Link>
      </p>
    </div>
  )
}

export default LoginPage
