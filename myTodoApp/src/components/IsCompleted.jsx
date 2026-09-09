function IsCompleted({ todo, onDelete, onComplete }) {

    return (
        <li id="task-list-single-el">

            <label>
                <input
                    type="checkbox"
                    id="checkbox-el"
                    checked={todo.completed}
                    onChange={(event) =>
                        onComplete(
                            todo.id,
                            event.target.checked
                        )
                    }
                />
            </label>

            <span className="task-text-el is-completed">     
                {todo.task}
            </span>

            <button
                type="button"
                id="clearBtn"
                aria-label="Delete todo"
                onClick={() => onDelete(todo.id)}
            >
                &times;
            </button>

        </li>
    )
}

export default IsCompleted