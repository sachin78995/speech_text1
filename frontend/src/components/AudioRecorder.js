import React, { useState, useRef } from 'react';
import './AudioRecorder.css';

const API_BASE_URL = 'http://localhost:8000/api';

const AudioRecorder = ({ onTranscriptCreated }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  const startRecording = async () => {
    try {
      setError(null);
      audioChunksRef.current = [];
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(track => track.stop());
        processRecording();
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      
      // Start timer
      setRecordingTime(0);
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      setError('Failed to access microphone. Please check permissions.');
      console.error('Error starting recording:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const processRecording = async () => {
    try {
      setIsProcessing(true);
      
      // Convert audio chunks to WAV format
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      console.log('DEBUG: Audio Blob before WAV conversion:', audioBlob); // Added logging
      const wavBlob = await convertToWav(audioBlob);
      console.log('DEBUG: WAV Blob after conversion:', wavBlob); // Added logging
      
      // Create form data
      const formData = new FormData();
      formData.append('audio', wavBlob, 'recording.wav');
      
      // Send to backend
      const response = await fetch(`${API_BASE_URL}/transcribe/`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to process audio');
      }
      
      const transcript = await response.json();
      onTranscriptCreated(transcript);
      
    } catch (err) {
      setError('Failed to process recording. Please try again.');
      console.error('Error processing recording:', err);
    } finally {
      setIsProcessing(false);
      setRecordingTime(0);
    }
  };

  const convertToWav = async (audioBlob) => {
    return new Promise((resolve) => {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      const fileReader = new FileReader();
      console.log('DEBUG: AudioContext sample rate:', audioContext.sampleRate); // Added logging

      fileReader.onloadend = () => {
        const arrayBuffer = fileReader.result;
        audioContext.decodeAudioData(arrayBuffer, async (audioBuffer) => {
          const wavBuffer = await encodeWAV(audioBuffer);
          const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });
          resolve(wavBlob);
        });
      };
      fileReader.readAsArrayBuffer(audioBlob);
    });
  };

  const floatTo16BitPCM = (output, offset, input) => {
    for (let i = 0; i < input.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, input[i]));
      output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
  };

  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  const encodeWAV = async (audioBuffer) => {
    const numOfChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;
    
    let length = audioBuffer.length * numOfChannels * 2; // 2 bytes per sample

    const buffer = new ArrayBuffer(44 + length);
    const view = new DataView(buffer);

    // RIFF chunk descriptor
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + length, true);
    writeString(view, 8, 'WAVE');

    // FMT chunk
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numOfChannels * (bitDepth / 8), true);
    view.setUint16(32, numOfChannels * (bitDepth / 8), true);
    view.setUint16(34, bitDepth, true);

    // DATA chunk
    writeString(view, 36, 'data');
    view.setUint32(40, length, true);

    let offset = 44;
    for (let i = 0; i < numOfChannels; i++) {
      floatTo16BitPCM(view, offset, audioBuffer.getChannelData(i));
      offset += audioBuffer.getChannelData(i).length * 2;
    }

    return buffer;
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <div className="audio-recorder">
      {error && (
        <div className="recorder-error fade-in">
          <span>{error}</span>
          <button onClick={clearError} className="error-close">×</button>
        </div>
      )}
      
      <div className="recorder-controls">
        {!isRecording && !isProcessing && (
          <button 
            className="record-button pulse"
            onClick={startRecording}
          >
            <span className="record-icon">🎤</span>
            <span>Start Recording</span>
          </button>
        )}
        
        {isRecording && (
          <button 
            className="stop-button recording"
            onClick={stopRecording}
          >
            <span className="stop-icon">⏹️</span>
            <span>Stop Recording</span>
          </button>
        )}
        
        {isProcessing && (
          <div className="processing">
            <div className="processing-spinner"></div>
            <span>Processing audio...</span>
          </div>
        )}
      </div>
      
      {isRecording && (
        <div className="recording-info fade-in">
          <div className="recording-indicator">
            <div className="recording-dot"></div>
            <span>Recording...</span>
          </div>
          <div className="recording-time">
            {formatTime(recordingTime)}
          </div>
        </div>
      )}
      
      <div className="recorder-tips">
        <h3>💡 Tips for better results:</h3>
        <ul>
          <li>Speak clearly and at a normal pace</li>
          <li>Minimize background noise</li>
          <li>Keep the microphone close to your mouth</li>
          <li>Record in a quiet environment</li>
        </ul>
      </div>
    </div>
  );
};

export default AudioRecorder;

