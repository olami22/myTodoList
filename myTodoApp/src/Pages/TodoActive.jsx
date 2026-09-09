import { useEffect, useState } from "react"
import axios from "axios"
import IsActive from "../components/IsActive.jsx"


function TodoActive({ onDelete, onComplete,todo }) {
  

  return (
    <>
    <div className="todo-body">
        {todo.length === 0 && <p>No todos found.</p>}
        <ul id="task-list-el">
            {todo
            .filter((item) => !item.completed)
            .map((item) => (
                <IsActive
                    key={item.id}
                    todo={item}
                    onDelete={onDelete}
                    onComplete={onComplete}
                />
            ))}
        </ul>
    </div>
    </>
  )
}

export default TodoActive