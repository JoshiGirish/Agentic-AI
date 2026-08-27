import { Routes, Route, Navigate } from 'react-router-dom'
import { Home } from './pages/Home'
import { Conversation } from './pages/Conversation'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/home" replace />} />
      <Route path="/home" element={<Home />} />
      <Route path="/conversation/:id" element={<Conversation />} />
    </Routes>
  )
}
