import { useEffect, useState } from "react"
import axios from "axios"
import TodoItem from "../components/TodoItem"


function Todo({ onComplete, onDelete,todo }) {
 
    
  return (
    <>
    <div className="todo-body">
        {todo.length === 0 && <p>No todos found.</p>}
        <ul id="task-list-el">
            {todo.map((item) => (
                <TodoItem
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

export default Todo