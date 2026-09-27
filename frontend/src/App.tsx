import Emoji from './components/Emoji.tsx'
import UploadPage from './pages/UploadPage.tsx'
import SharePage from './pages/SharePage.tsx'

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
