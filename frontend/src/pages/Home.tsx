export default function Home() {
  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem' }}>
      <div style={{ marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
          Government Feed
        </h1>
        <p style={{ fontSize: '1.1rem', color: '#666' }}>
          Sistema di aggregazione e analisi di feed istituzionali
        </p>
      </div>

      <div
        style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '2rem',
        }}
      >
        <h2 style={{ marginBottom: '1rem' }}>Benvenuto</h2>
        <p style={{ color: '#666', marginBottom: '1rem' }}>
          Inizia configurando i tuoi feed nella sezione{' '}
          <a href="/sources" style={{ color: '#1976d2' }}>
            Gestione Sources
          </a>
          .
        </p>
        <p style={{ color: '#666' }}>
          Poi vai su{' '}
          <a href="/feed" style={{ color: '#1976d2' }}>
            Feed Reader
          </a>{' '}
          per vedere le notizie.
        </p>
      </div>
    </div>
  )
}
