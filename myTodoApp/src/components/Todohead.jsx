import { useState } from 'react'
import axios from "axios"
import { Link } from 'react-router-dom'

function Todohead({ onTaskAdded, activeCount, completedCount }) {

    const today = new Date()
    const options = { month: 'long', day: 'numeric' }
    const formattedDate = today.toLocaleDateString('en-US', options)

    const [task, setTask] = useState('')

    async function handleAddTask(){
        if (!task.trim()) return

        await axios.post("http://127.0.0.1:8000/todo",
            {
                "task": task
            }
        )
        let message = document.getElementById("show-info");
        message.textContent = "Task Added!";

        setTimeout(() => {
            message.textContent = "";
        }, 5000);
        setTask('')
        onTaskAdded()
    }

  return (
    <>
        <div className="todo-body">
            <nav>
                <p id="show-info"></p>
            </nav>
            <div className="todo-heading">
                <h4 id="today-date">{formattedDate}</h4>
                <h3 id="greeting"> Welcome, 'Username'!</h3>
                <h1 id="task-head">Tasks</h1>
            </div>
                
            <div>
                <p id="num-task"> <span id="num-task-remain"> { activeCount } </span>remaining  <span id="num-task-done">  { completedCount } </span>done </p>
                <input id="task-input" type="text" placeholder="Add a new task..."
                  value={task}
                  onChange={(event)=>setTask(event.target.value)}/>

                <button id="add-task-btn" onClick={() => handleAddTask()}
                > Add </button>
                <div className="task-state">
                    <p><Link to ="/" id="all-link">ALL</Link></p>
                    <p><Link to ="/active" id="active-link">ACTIVE</Link></p>
                    <p><Link to ="/complete" id="complete-link">COMPLETED</Link></p>
                </div>

            </div>

            

        </div>
    </>
  )
}

export default Todohead;