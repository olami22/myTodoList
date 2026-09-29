import IsCompleted from "../components/IsCompleted.jsx"


function TodoComplete({ todo, onDelete, onComplete }) {
  
  return (
    <>
    <div className="todo-body">
        {todo.length === 0 && <p>No todos found.</p>}
        <ul id="task-list-el">
            {todo
            .filter((item) => item.completed)
            .map((item) => (
                <IsCompleted
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

export default TodoComplete