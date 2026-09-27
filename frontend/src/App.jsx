import UploadPage from './pages/UploadPage.jsx'
import SharePage from './pages/SharePage.jsx'

function App() {
  const shareMatch = window.location.pathname.match(/^\/share\/([^/]+)\/?$/)

  return (
    <>
      <header>
        <a href="/">ShareIT</a>
      </header>
      <main>
        {shareMatch ? <SharePage shareId={shareMatch[1]} /> : <UploadPage />}
      </main>
    </>
  )
}

export default App
