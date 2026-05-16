import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router'
import RootPage from './pages/page'
import AboutPage from './pages/about/page'
import "./index.css"

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<RootPage />} index />
        <Route path='/about' element={<AboutPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
