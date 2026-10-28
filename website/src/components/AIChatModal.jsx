import React, { useState, useEffect, useRef } from 'react';
import { 
  X, Send, Mic, MicOff, Volume2, Sparkles, Bot, User, Loader2 
} from 'lucide-react';
import { api } from '../api/client';
import { translations } from '../i18n/translations';

export default function AIChatModal({ isOpen, onClose, weather, language }) {
  const t = translations[language] || translations.en;

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: language === 'hi' 
        ? "नमस्ते! मैं WeatherGPT सहायक हूँ। मौसम, वर्षा, कपड़े, कृषि या यात्रा के बारे में कोई भी प्रश्न पूछें।" 
        : language === 'mr'
        ? "नमस्कार! मी WeatherGPT सहाय्यक आहे. हवामान, पाऊस, शेती सल्ला किंवा प्रवासाबद्दल काहीही विचारा."
        : "Hello! I am WeatherGPT Assistant. Ask me anything about current weather, rain, clothing advice, farming, or travel.",
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);

  const quickPills = language === 'hi' ? [
    "क्या कल बारिश होगी?",
    "आज क्या पहनना चाहिए?",
    "पुणे और मुंबई के मौसम की तुलना करें",
    "किसानों के लिए क्या सलाह है?",
    "आज बाहर जाना ठीक रहेगा क्या?",
  ] : language === 'mr' ? [
    "उद्या पाऊस पडेल का?",
    "आज कोणते कपडे घालावे?",
    "पुणे आणि मुंबई हवामानाची तुलना करा",
    "शेतीसाठी आजचा सल्ला काय आहे?",
    "आज बाहेर फिरणे योग्य आहे का?",
  ] : [
    "Will it rain tomorrow?",
    "What should I wear today?",
    "Compare Pune and Mumbai weather",
    "Agricultural weather advisory",
    "Is it a good time to go outside?",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  // Voice Input (Web Speech API)
  const toggleListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert(t.speechNotSupported);
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = language === 'hi' ? 'hi-IN' : language === 'mr' ? 'mr-IN' : 'en-US';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onerror = () => setIsListening(false);

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        handleSend(transcript);
      };

      recognition.start();
    } catch (err) {
      console.error('Speech recognition error:', err);
      setIsListening(false);
    }
  };

  // Text-to-Speech Output
  const speakText = (text) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'hi' ? 'hi-IN' : language === 'mr' ? 'mr-IN' : 'en-US';
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async (messageToSend) => {
    const text = (messageToSend || input).trim();
    if (!text || isLoading) return;

    setInput('');
    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const res = await api.sendChatMessage({
        message: text,
        language,
        latitude: weather?.latitude,
        longitude: weather?.longitude,
        location_name: weather?.location_name,
      });

      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: res.reply,
          facts: res.grounded_facts,
          suggestions: res.suggestions,
        }
      ]);
    } catch (err) {
      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: language === 'hi'
            ? "क्षमा करें, सर्वर से उत्तर प्राप्त करने में समस्या हुई। कृपया पुनः प्रयास करें।"
            : language === 'mr'
            ? "क्षमस्व, सर्व्हरशी संपर्क साधता आला नाही. कृपया पुन्हा प्रयत्न करा."
            : "Sorry, I encountered an issue retrieving the weather intelligence. Please retry.",
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-slate-950/60 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-lg h-full bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col justify-between">
        
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90 backdrop-blur-md">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 text-white shadow-md shadow-sky-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">
                {t.aiAssistant}
              </h2>
              <p className="text-xs text-sky-400">
                {weather?.location_name ? `Grounded in ${weather.location_name}` : 'Ready for queries'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-3 ${
                msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                  msg.role === 'user'
                    ? 'bg-sky-500 text-white'
                    : 'bg-slate-800 border border-slate-700 text-sky-400'
                }`}
              >
                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-sky-500 text-white rounded-tr-none'
                    : 'bg-slate-800/90 text-slate-200 border border-slate-700/60 rounded-tl-none shadow-md'
                }`}
              >
                <p className="whitespace-pre-line">{msg.content}</p>

                {msg.role === 'assistant' && (
                  <div className="mt-2.5 pt-2 border-t border-slate-700/40 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="flex items-center gap-1 text-emerald-400">
                      ✓ Verified Real Weather Data
                    </span>
                    <button
                      onClick={() => speakText(msg.content)}
                      title="Read aloud"
                      className="p-1 hover:text-sky-400 rounded-md transition-colors"
                    >
                      <Volume2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-sky-400 shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-800/80 rounded-2xl px-4 py-3 border border-slate-700/60 flex items-center gap-2 text-slate-400 text-xs">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-400" />
                <span>Grounding meteorological answer...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompt Pills */}
        <div className="px-4 py-2 border-t border-slate-800 bg-slate-900/60 flex gap-2 overflow-x-auto scrollbar-none">
          {quickPills.map((pill, i) => (
            <button
              key={i}
              onClick={() => handleSend(pill)}
              className="px-3 py-1.5 rounded-full bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs border border-slate-700/80 whitespace-nowrap transition-colors"
            >
              {pill}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/90">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <button
              type="button"
              onClick={toggleListening}
              className={`p-2.5 rounded-xl border transition-all ${
                isListening
                  ? 'bg-rose-500 text-white border-rose-400 animate-pulse'
                  : 'bg-slate-800 text-slate-400 hover:text-white border-slate-700'
              }`}
              title="Voice Input"
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t.chatPlaceholder}
              className="flex-1 bg-slate-800 text-slate-100 text-sm rounded-xl px-4 py-2.5 border border-slate-700 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
            />

            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="p-2.5 bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-white rounded-xl shadow-md transition-all"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
