import { useState, useEffect, useRef, useCallback } from 'react';

export const useVoice = (onTranscript, onError) => {
  const [isListening, setIsListening] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const recognitionRef = useRef(null);
  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const queueRef = useRef([]);
  const currentSourceRef = useRef(null);
  const isPlayingRef = useRef(false);

  // Initialize Audio Context and Analyser
  useEffect(() => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const audioCtx = new AudioContext();
    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.8;
    analyser.connect(audioCtx.destination);
    
    audioCtxRef.current = audioCtx;
    analyserRef.current = analyser;

    return () => {
      audioCtx.close();
    };
  }, []);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      onError?.("Speech recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          const text = event.results[i][0].transcript.trim();
          if (text) onTranscript?.(text);
        }
      }
    };

    recognition.onend = () => {
      if (isListening) {
        try {
          recognition.start();
        } catch (e) {
          // Already started
        }
      }
    };

    recognition.onerror = (event) => {
      if (event.error === "not-allowed") {
        onError?.("Microphone access denied. Please allow microphone access.");
        setIsListening(false);
      } else if (event.error === "no-speech") {
        // Normal, just restart
      } else if (event.error === "aborted") {
        // Expected during pause
      } else {
        console.warn("[voice] recognition error:", event.error);
      }
    };

    recognitionRef.current = recognition;
  }, [onTranscript, onError, isListening]);

  const startListening = useCallback(() => {
    setIsListening(true);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch (e) {}
    }
  }, []);

  const stopListening = useCallback(() => {
    setIsListening(false);
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  const playNext = useCallback(async () => {
    if (queueRef.current.length === 0) {
      isPlayingRef.current = false;
      setIsPlaying(false);
      currentSourceRef.current = null;
      return;
    }

    isPlayingRef.current = true;
    setIsPlaying(true);
    const buffer = queueRef.current.shift();
    const source = audioCtxRef.current.createBufferSource();
    source.buffer = buffer;
    source.connect(analyserRef.current);
    currentSourceRef.current = source;

    source.onended = () => {
      if (currentSourceRef.current === source) {
        playNext();
      }
    };

    source.start();
  }, []);

  const enqueueAudio = useCallback(async (base64) => {
    if (audioCtxRef.current.state === "suspended") {
      await audioCtxRef.current.resume();
    }

    try {
      const binary = atob(base64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }
      const audioBuffer = await audioCtxRef.current.decodeAudioData(bytes.buffer.slice(0));
      queueRef.current.push(audioBuffer);
      if (!isPlayingRef.current) playNext();
    } catch (err) {
      console.error("[audio] decode error:", err);
      if (!isPlayingRef.current && queueRef.current.length > 0) playNext();
    }
  }, [playNext]);

  const stopAudio = useCallback(() => {
    queueRef.current = [];
    if (currentSourceRef.current) {
      try {
        currentSourceRef.current.stop();
      } catch (e) {}
      currentSourceRef.current = null;
    }
    isPlayingRef.current = false;
    setIsPlaying(false);
  }, []);

  return {
    isListening,
    isPlaying,
    startListening,
    stopListening,
    enqueueAudio,
    stopAudio,
    analyser: analyserRef.current
  };
};
