import React, { useState } from 'react';
import './TranscriptList.css';

const TranscriptList = ({ transcripts, onDelete }) => {
  const [expandedId, setExpandedId] = useState(null);

  const toggleExpanded = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this transcript?')) {
      await onDelete(id);
    }
  };

  if (transcripts.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📝</div>
        <h3>No transcripts yet</h3>
        <p>Start recording to see your transcripts here!</p>
      </div>
    );
  }

  return (
    <div className="transcript-list">
      {transcripts.map((transcript) => (
        <div 
          key={transcript.id} 
          className={`transcript-item fade-in ${expandedId === transcript.id ? 'expanded' : ''}`}
          onClick={() => toggleExpanded(transcript.id)}
        >
          <div className="transcript-header">
            <div className="transcript-info">
              <div className="transcript-date">
                {formatDate(transcript.created_at)}
              </div>
              <div className="transcript-preview">
                {transcript.corrected_text.length > 100 
                  ? `${transcript.corrected_text.substring(0, 100)}...` 
                  : transcript.corrected_text
                }
              </div>
            </div>
            <div className="transcript-actions">
              <button 
                className="expand-button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleExpanded(transcript.id);
                }}
              >
                {expandedId === transcript.id ? '−' : '+'}
              </button>
              <button 
                className="delete-button"
                onClick={(e) => handleDelete(transcript.id, e)}
                title="Delete transcript"
              >
                🗑️
              </button>
            </div>
          </div>
          
          {expandedId === transcript.id && (
            <div className="transcript-details">
              <div className="text-section">
                <h4>Original Transcription:</h4>
                <div className="text-content original">
                  {transcript.converted_text || 'No text available'}
                </div>
              </div>
              
              <div className="text-section">
                <h4>Grammar Corrected:</h4>
                <div className="text-content corrected">
                  {transcript.corrected_text || 'No text available'}
                </div>
              </div>
              
              {transcript.audio_filename && (
                <div className="audio-section">
                  <h4>Audio File:</h4>
                  <div className="audio-info">
                    <span className="audio-filename">{transcript.audio_filename}</span>
                    <a 
                      href={`/media/${transcript.original_audio}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="audio-download"
                      onClick={(e) => e.stopPropagation()}
                    >
                      Download Audio
                    </a>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default TranscriptList;

