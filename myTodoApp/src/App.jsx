import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { api } from './api/client.js'
import { useAuth } from './features/auth/useAuth.js'
import { useNotes } from './features/notes/useNotes.js'
import Todohead from './components/Todohead.jsx'
import Todo from './Pages/Todo.jsx'
import TodoActive from './Pages/TodoActive.jsx'
import TodoComplete from './Pages/TodoComplete.jsx'
import LoginPage from './Pages/Login.jsx'
import RegisterPage from './Pages/Register.jsx'
import NotesPanel from './components/NotesPanel.jsx'
import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom'

function App() {
  const [todo, setTodo] = useState([])
  const [error, setError] = useState('')
  const { currentUser, isAuthenticated, isLoading, login, register, logout } = useAuth()
  const { notes, addNote, deleteNote } = useNotes(isAuthenticated)

  const fetchTodo = useCallback(async () => {
    if (!isAuthenticated) {
      setTodo([])
      return
    }

    try {
      const { data } = await api.get('/')
      setTodo(data)
      setError('')
    } catch (requestError) {
      setError('Could not load todos.')
      console.error(requestError)
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (isAuthenticated) {
      fetchTodo()
    }
  }, [isAuthenticated, fetchTodo])

  async function deleteTodo(todoId) {
    await api.delete(`/todo/${todoId}`)
  }

  async function updateTodo(todoId, completed) {
    await api.put(`/todo/${todoId}`, {
      completed: completed,
    })
  }

  function handleTaskAdded() {
    fetchTodo()
  }

  async function handleDelete(todoId) {
    try {
      await deleteTodo(todoId)
      setTodo((currentTodos) => currentTodos.filter((item) => item.id !== todoId))
    } catch (requestError) {
      setError('Could not delete todo.')
      console.error(requestError)
    }
  }

  async function handleCompletionChange(todoId, completed) {
    try {
      await updateTodo(todoId, completed)

      setTodo((currentTodos) =>
        currentTodos.map((item) =>
          item.id === todoId ? { ...item, completed: completed } : item
        )
      )
    } catch (requestError) {
      setError('Could not update todo.')
      console.error(requestError)
    }
  }

  async function handleLogin(username, password) {
    return login(username, password)
  }

  async function handleRegister(username, password) {
    await register(username, password)
  }

  async function handleLogout() {
    await logout()
    setTodo([])
  }

  async function handleAddNote({ title, content }) {
    await addNote({ title, content })
  }

  async function handleDeleteNote(noteId) {
    await deleteNote(noteId)
  }

  const activeCount = todo.filter((item) => !item.completed).length
  const completedCount = todo.filter((item) => item.completed).length

  if (isLoading) {
    return (
      <main className="auth-page" role="status" aria-live="polite">
        Checking your session...
      </main>
    )
  }

  return (
    <Router>
      {isAuthenticated && (
        <Todohead
          onTaskAdded={handleTaskAdded}
          activeCount={activeCount}
          completedCount={completedCount}
          currentUser={currentUser}
        />
      )}

      {error && <p className="app-error">{error}</p>}

      <Routes>
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage onLogin={handleLogin} />}
        />

        <Route
          path="/register"
          element={isAuthenticated ? <Navigate to="/" replace /> : <RegisterPage onRegister={handleRegister} />}
        />

        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Todo
                todo={todo}
                onDelete={handleDelete}
                onComplete={handleCompletionChange}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/complete"
          element={
            isAuthenticated ? (
              <TodoComplete
                todo={todo}
                onDelete={handleDelete}
                onComplete={handleCompletionChange}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/active"
          element={
            isAuthenticated ? (
              <TodoActive
                todo={todo}
                onDelete={handleDelete}
                onComplete={handleCompletionChange}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>

      {isAuthenticated && (
        <div className="todo-body notes-section">
          <NotesPanel
            notes={notes}
            onAddNote={handleAddNote}
            onDeleteNote={handleDeleteNote}
          />
          <button type="button" className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      )}
        
    </Router>
  )
}

export default App
