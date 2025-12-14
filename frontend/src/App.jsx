import React, { useState } from 'react';
import './index.css';
import { Upload, Search, ShieldCheck, Database, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';

const API_URL = "http://127.0.0.1:8001";

function App() {
  const [currentMode, setCurrentMode] = useState('menu'); // menu, match, internet, ai

  const renderContent = () => {
    switch (currentMode) {
      case 'menu': return <MainMenu setMode={setCurrentMode} />;
      case 'match': return <ImageMatcher goBack={() => setCurrentMode('menu')} />;
      case 'internet': return <InternetCheck goBack={() => setCurrentMode('menu')} />;
      case 'ai': return <AIDetector goBack={() => setCurrentMode('menu')} />;
      default: return <MainMenu setMode={setCurrentMode} />;
    }
  }

  return (
    <div className="app-container">
      <header className="blur-header">
        <h1>Vision Verify</h1>
        {currentMode !== 'menu' && (
          <button className="back-btn" onClick={() => setCurrentMode('menu')}>
            Back to Menu
          </button>
        )}
      </header>
      <main className="main-content">
        {renderContent()}
      </main>
    </div>
  );
}

const MainMenu = ({ setMode }) => (
  <div className="menu-grid">
    <div className="card menu-card" onClick={() => setMode('match')}>
      <div className="icon-wrapper"><Database size={48} /></div>
      <h2>Identity Match</h2>
      <p>Compare images against a personal database.</p>
    </div>
    <div className="card menu-card" onClick={() => setMode('internet')}>
      <div className="icon-wrapper"><Search size={48} /></div>
      <h2>Internet Check</h2>
      <p>Scan the web for image sources.</p>
    </div>
    <div className="card menu-card" onClick={() => setMode('ai')}>
      <div className="icon-wrapper"><ShieldCheck size={48} /></div>
      <h2>AI Detection</h2>
      <p>Analyze for AI manipulation.</p>
    </div>
  </div>
);

const ImageMatcher = ({ goBack }) => {
  const [uploadStatus, setUploadStatus] = useState('');
  const [result, setResult] = useState(null);

  const handleDbUpload = async (e) => {
    const files = e.target.files;
    if (!files.length) return;
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    setUploadStatus('Uploading...');
    try {
      const res = await fetch(`${API_URL}/upload_references`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setUploadStatus(data.message);
    } catch (err) {
      setUploadStatus('Error uploading files. Is the server running?');
    }
  };

  const handleMatchUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setResult({ loading: true });
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/match_image`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: 'Failed to connect to server.' });
    }
  }

  return (
    <div className="feature-wrapper">
      <button className="secondary-btn back-top" onClick={goBack}>&larr; Back to Menu</button>

      <div className="matcher-grid">
        {/* Left Column: Database */}
        <div className="matcher-col">
          <div className="step-header">
            <Database size={32} className="step-icon" />
            <h3>Step 1: Database</h3>
          </div>
          <p>Upload reference images (max 100).</p>

          <div className="upload-options">
            <div className="upload-zone">
              <input type="file" multiple onChange={handleDbUpload} id="db-upload" className="hidden-input" />
              <label htmlFor="db-upload" className="upload-btn">Select Files</label>
            </div>

            <div className="divider">OR</div>

            <div className="drive-input-group">
              <input
                type="text"
                placeholder="Paste Public Drive Folder Link"
                onKeyDown={async (e) => {
                  if (e.key === 'Enter') {
                    setUploadStatus('Importing from Drive...');
                    try {
                      const res = await fetch(`${API_URL}/import_drive`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ link: e.target.value })
                      });
                      const data = await res.json();
                      setUploadStatus(data.message || data.error);
                    } catch (err) {
                      setUploadStatus('Import failed.');
                    }
                  }
                }}
                className="text-input"
              />
              <p className="hint">Press Enter to import</p>
            </div>
          </div>

          {uploadStatus && <div className="status-msg">{uploadStatus}</div>}
        </div>

        {/* Right Column: Match */}
        <div className="matcher-col">
          <div className="step-header">
            <Search size={32} className="step-icon" />
            <h3>Step 2: Match</h3>
          </div>
          <p>Upload an image to compare.</p>
          <div className="upload-zone">
            <input type="file" onChange={handleMatchUpload} id="match-upload" className="hidden-input" />
            <label htmlFor="match-upload" className="upload-btn">Select Image</label>
          </div>

          {result && result.loading && <div className="loader small">Analyzing...</div>}

          {result && !result.loading && (
            <div className="result-display">
              {result.error ? (
                <div className="error">{result.error}</div>
              ) : (
                <div className={`score-card ${result.is_match ? 'success' : 'fail'}`}>
                  <div className="score-val small">{result.score}/10</div>
                  <div className="score-label">{result.is_match ? 'MATCH' : 'NO MATCH'}</div>
                  {result.match_found && <div className="match-name">{result.best_match_filename}</div>}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const InternetCheck = ({ goBack }) => {
  const [result, setResult] = useState(null);

  const handleCheck = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setResult({ loading: true });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/check_internet`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: "Failed to connect to server. Is the backend running?" });
    }
  }

  return (
    <div className="feature-container">
      <h2>Internet Source Check</h2>
      <p>Upload an image to see if it exists online.</p>
      <input type="file" onChange={handleCheck} className="file-input" />

      {result && result.loading && <div className="loader">Scanning web...</div>}
      {result && result.error && <div className="error">{result.error}</div>}

      {result && !result.loading && !result.error && (
        <div className="result-box">
          <h3>Internet Trace Score: {result.score}/10</h3>
          {result.found_on_internet ? (
            <div className="trace-found">
              <span className="badge warning">Found Online</span>
              <ul>
                {result.sources.map(s => <li key={s}>{s}</li>)}
              </ul>
            </div>
          ) : (
            <span className="badge success">Unique Image</span>
          )}
        </div>
      )}
      <button className="secondary-btn" onClick={goBack}>&larr; Back</button>
    </div>
  )
}

const AIDetector = ({ goBack }) => {
  const [result, setResult] = useState(null);

  const handleCheck = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setResult({ loading: true });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/check_ai`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: "Failed to connect to server. Is the backend running?" });
    }
  }

  return (
    <div className="feature-container">
      <h2>AI Manipulation Detector</h2>
      <p>Analyze invisible noise patterns.</p>
      <input type="file" onChange={handleCheck} className="file-input" />

      {result && result.loading && <div className="loader">Analyzing artifacts...</div>}
      {result && result.error && <div className="error">{result.error}</div>}

      {result && !result.loading && !result.error && (
        <div className="result-box">
          <h3>Confidence: {result.confidence_score}%</h3>
          {result.is_ai_generated ? (
            <div className="ai-alert">
              <AlertTriangle size={32} color="red" />
              <span>Likely AI Generated</span>
            </div>
          ) : (
            <div className="human-badge">
              <CheckCircle size={32} color="green" />
              <span>Likely Real</span>
            </div>
          )}
          <p className="details">{result.details}</p>
        </div>
      )}
      <button className="secondary-btn" onClick={goBack}>&larr; Back</button>
    </div>
  )
}

export default App;
