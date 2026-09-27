import Emoji from './components/Emoji.jsx'
import UploadPage from './pages/UploadPage.jsx'
import SharePage from './pages/SharePage.jsx'

function App() {
  const shareMatch = window.location.pathname.match(/^\/share\/([^/]+)\/?$/)

  return (
    <>
      <header className="site-header">
        <a className="brand" href="/">
          <Emoji>🔗</Emoji> ShareIT
        </a>
      </header>
      <main>
        {shareMatch ? <SharePage shareId={shareMatch[1]} /> : <UploadPage />}
      </main>
    </>
  )
}

export default App
