import React, { useState, useEffect } from 'react';
import './App.css';
import AudioRecorder from './components/AudioRecorder';
import TranscriptList from './components/TranscriptList';
import Header from './components/Header';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [transcripts, setTranscripts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch transcripts on component mount
  useEffect(() => {
    fetchTranscripts();
  }, []);

  const fetchTranscripts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/transcripts/`);
      if (response.ok) {
        const data = await response.json();
        setTranscripts(data);
      } else {
        throw new Error('Failed to fetch transcripts');
      }
    } catch (err) {
      setError('Failed to load transcripts');
      console.error('Error fetching transcripts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNewTranscript = (newTranscript) => {
    setTranscripts([newTranscript, ...transcripts]);
  };

  const handleDeleteTranscript = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/transcripts/${id}/`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setTranscripts(transcripts.filter(t => t.id !== id));
      } else {
        throw new Error('Failed to delete transcript');
      }
    } catch (err) {
      setError('Failed to delete transcript');
      console.error('Error deleting transcript:', err);
    }
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <div className="App">
      <Header />
      
      <main className="main-content">
        <div className="container">
          {/* Error Message */}
          {error && (
            <div className="error-message fade-in">
              <span>{error}</span>
              <button onClick={clearError} className="error-close">×</button>
            </div>
          )}

          {/* Audio Recorder Section */}
          <section className="recorder-section fade-in">
            <h2>🎤 Record Your Speech</h2>
            <p>Click the button below to start recording. Speak clearly for better results.</p>
            <AudioRecorder onTranscriptCreated={handleNewTranscript} />
          </section>

          {/* Transcripts Section */}
          <section className="transcripts-section fade-in">
            <h2>📝 Your Transcripts</h2>
            {loading ? (
              <div className="loading">
                <div className="spinner"></div>
                <p>Loading transcripts...</p>
              </div>
            ) : (
              <TranscriptList 
                transcripts={transcripts} 
                onDelete={handleDeleteTranscript}
              />
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;

