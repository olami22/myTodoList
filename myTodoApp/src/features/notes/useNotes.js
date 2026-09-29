import { useCallback, useEffect, useState } from 'react'

import { api } from '../../api/client'

export function useNotes(token) {
  const [notes, setNotes] = useState([])

  const refreshNotes = useCallback(async () => {
    if (!token) {
      setNotes([])
      return
    }

    try {
      const { data } = await api.get('/notes')
      setNotes(data)
    } catch (requestError) {
      console.error(requestError)
    }
  }, [token])

  useEffect(() => {
    if (token) {
      refreshNotes()
      return
    }

    setNotes([])
  }, [token, refreshNotes])

  const addNote = useCallback(async ({ title, content }) => {
    const { data } = await api.post('/notes', { title, content })
    setNotes((currentNotes) => [data, ...currentNotes])
    return data
  }, [])

  const deleteNote = useCallback(async (noteId) => {
    await api.delete(`/notes/${noteId}`)
    setNotes((currentNotes) => currentNotes.filter((note) => note.id !== noteId))
  }, [])

  return {
    notes,
    addNote,
    deleteNote,
    refreshNotes,
  }
}
