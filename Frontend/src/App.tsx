import './App.css'
import { Chat } from './pages/chat/chat'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext'
import { WebSocketProvider } from './context/WebsocketContext';


function App() {
  return (
    <ThemeProvider>
      <WebSocketProvider>
        <Router>
          <div className="w-full h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
            <Routes>
              <Route path="/" element={<Chat />} />
            </Routes>
          </div>
        </Router>
      </WebSocketProvider>
    </ThemeProvider>
  )
}

export default App;