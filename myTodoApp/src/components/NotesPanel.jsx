import { useState } from 'react'

function NotesPanel({ notes, onAddNote, onDeleteNote }) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    if (!title.trim() || !content.trim()) return

    await onAddNote({ title: title.trim(), content: content.trim() })
    setTitle('')
    setContent('')
  }

  return (
    <div className="note-panel">
      <h3>Notes</h3>

      <form className="note-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Note title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
        <textarea
          placeholder="Write a note..."
          value={content}
          onChange={(event) => setContent(event.target.value)}
        />
        <button type="submit">Add note</button>
      </form>

      {notes.length === 0 ? (
        <p className="empty-notes">No notes yet.</p>
      ) : (
        <ul className="note-list">
          {notes.map((note) => (
            <li key={note.id} className="note-item">
              <h4>{note.title}</h4>
              <p>{note.content}</p>
              <button type="button" onClick={() => onDeleteNote(note.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default NotesPanel
