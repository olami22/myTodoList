import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'

function Todohead({ onTaskAdded, activeCount, completedCount, currentUser }) {
  const today = new Date()
  const options = { month: 'long', day: 'numeric' }
  const formattedDate = today.toLocaleDateString('en-US', options)

  const [task, setTask] = useState('')

  async function handleAddTask() {
    if (!task.trim()) return

    await api.post('/todo', { task })

    const message = document.getElementById('show-info')
    if (message) {
      message.textContent = 'Task Added!'
      setTimeout(() => {
        message.textContent = ''
      }, 5000)
    }

    setTask('')
    onTaskAdded()
  }

  return (
    <div className="todo-body">
      <nav>
        <p id="show-info"></p>
      </nav>
      <div className="todo-heading">
        <h4 id="today-date">{formattedDate}</h4>
        <h3 id="greeting"> Welcome, {currentUser || 'User'}!</h3>
        <h2 id="task-head">To-do List</h2>
      </div>

      <div>
        <p id="num-task">
          <span id="num-task-remain"> {activeCount} </span>remaining
          <span id="num-task-done"> {completedCount} </span>done
        </p>
        <input
          id="task-input"
          type="text"
          placeholder="Add a new task..."
          value={task}
          onChange={(event) => setTask(event.target.value)}
        />

        <button id="add-task-btn" onClick={handleAddTask}>Add</button>
        <div className="task-state">
          <p><Link to="/" id="all-link">ALL</Link></p>
          <p><Link to="/active" id="active-link">ACTIVE</Link></p>
          <p><Link to="/complete" id="complete-link">COMPLETED</Link></p>
        </div>
        <hr />
      </div>
    </div>
  )
}

export default Todohead;