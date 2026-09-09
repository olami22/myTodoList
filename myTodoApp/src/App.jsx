import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import Todohead from './components/Todohead.jsx'
import Todo from './Pages/Todo.jsx'
import TodoActive from './Pages/TodoActive.jsx'
import TodoComplete from './Pages/TodoComplete.jsx'
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom"

function App() {
  const [todo, setTodo] = useState([])
  const [error, setError] = useState('')

  async function deleteTodo(todoId) {
    await axios.delete(`http://127.0.0.1:8000/todo/${todoId}`)
  }

  async function updateTodo(todoId, completed) {
    await axios.put(`http://127.0.0.1:8000/todo/${todoId}`, 
      {
        "completed": completed
      }
    )   
  }

  async function fetchTodo(){
      try {
          const { data } = await axios.get("http://127.0.0.1:8000/")
          setTodo(data)
      } catch (requestError) {
          setError('Could not load todos.')
          console.error(requestError)
      }

      }

  useEffect(() => {
      fetchTodo()
  }, [])

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
              item.id === todoId
                  ? { ...item, completed: completed }
                  : item
          )
      )

  } catch (requestError) {
      setError('Could not update todo.')
      console.error(requestError)
  }
}
  const activeCount = todo.filter(
        (item) => !item.completed
    ).length

  const completedCount = todo.filter(
      (item) => item.completed
  ).length

  return (
    <>
      <Router>
        <Todohead 
          onTaskAdded={handleTaskAdded}
          activeCount={activeCount}
          completedCount={completedCount}
         />

        <Routes>
          <Route path="/" element={<Todo 
            todo={todo}
            onDelete={handleDelete}
            onComplete={handleCompletionChange}
            />}/>

          <Route path="/complete" element={<TodoComplete 
            todo={todo}
            onDelete={handleDelete}
            onComplete={handleCompletionChange}/>}/>
          
          <Route path="/active" element={<TodoActive
            todo={todo} 
            onDelete={handleDelete}
            onComplete={handleCompletionChange}/>}/>

        </Routes>
        
      </Router>
      
    </>
  )
}

export default App
