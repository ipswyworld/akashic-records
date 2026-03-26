import React, { useState, useEffect, useRef } from 'react';
import { 
  Paperclip, Send, BrainCircuit, Sparkles
} from 'lucide-react';
import { streamChat } from '../api';
import { getThemeColors } from '../components/CommonUI';

const ChatView = ({ messages, setMessages, isSynthesizing, setIsSynthesizing, theme, analytics }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const colors = getThemeColors(theme);

  useEffect(() => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }), [messages, isSynthesizing]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsSynthesizing(true);
    try {
      await streamChat(input, (token, full) => {
        setMessages(prev => {
          const last = prev[prev.length - 1];
          return last.role === 'ai' ? [...prev.slice(0, -1), { ...last, content: full }] : [...prev, { role: 'ai', content: full }];
        });
      });
    } catch (err) { setMessages(prev => [...prev, { role: 'ai', content: 'SYSTEM_ERROR: Neural core unreachable.' }]); } finally { setIsSynthesizing(false); }
  };

  return (
    <div className="flex flex-col h-full w-full max-w-4xl mx-auto relative animate-in fade-in">
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 hide-scrollbar relative">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} group relative`}>
            {msg.role === 'ai' && <div className={`w-8 h-8 rounded border flex items-center justify-center mr-3 mt-1 shrink-0 ${theme === 'dark' ? 'bg-slate-800 border-slate-700' : 'bg-white border-stone-200 shadow-sm'}`}><BrainCircuit className="w-4 h-4 text-amber-500" /></div>}
            <div className={`max-w-[85%] sm:max-w-[75%] relative ${msg.role === 'user' ? 'bg-blue-600 text-white shadow-md rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm sm:text-base' : `${colors.textMain} px-2 py-1 text-sm sm:text-base font-light`}`}>
              {msg.monologue && <div className="text-[10px] text-amber-500 italic mb-2 opacity-80 font-medium tracking-tight">Archivist: {msg.monologue}</div>}
              <div className="leading-relaxed whitespace-pre-wrap">{msg.content}</div>
            </div>
          </div>
        ))}
        
        {isSynthesizing && (
          <div className="flex justify-start animate-in fade-in slide-in-from-left-4 duration-500">
            <div className={`w-8 h-8 rounded border flex items-center justify-center mr-3 mt-1 shrink-0 ${theme === 'dark' ? 'bg-slate-800 border-slate-700' : 'bg-white border-stone-200 shadow-sm'}`}>
              <BrainCircuit className="w-4 h-4 text-amber-500 animate-pulse" />
            </div>
            <div className={`${theme === 'dark' ? 'bg-slate-900 border-slate-800' : 'bg-white border-stone-200 shadow-sm'} text-stone-400 px-4 py-2.5 rounded-2xl rounded-tl-sm text-xs sm:text-sm italic flex items-center`}>
              <span className="mr-2">Archivist is synthesizing</span>
              <span className="flex gap-1">
                <span className="w-1 h-1 bg-amber-500 rounded-full animate-bounce"></span>
                <span className="w-1 h-1 bg-amber-500 rounded-full animate-bounce delay-100"></span>
                <span className="w-1 h-1 bg-amber-500 rounded-full animate-bounce delay-200"></span>
              </span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      <div className={`shrink-0 border-t p-3 sm:p-4 z-20 ${theme === 'dark' ? 'bg-slate-950/95 border-slate-800' : 'bg-[#fcfaf7] border-stone-200'}`}>
        <div className={`relative flex items-end gap-2 border rounded-xl p-1.5 sm:p-2 focus-within:ring-2 focus-within:ring-amber-500/20 transition-all shadow-sm ${colors.inputBg} ${colors.panelBorder}`}>
          <button className="p-2 text-stone-400 hover:text-stone-600 shrink-0"><Paperclip className="w-4 h-4 sm:w-5 sm:h-5" /></button>
          <textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }} placeholder={`Talk to ${analytics?.neural_name || 'Archivist'}...`} className={`w-full bg-transparent border-none placeholder-stone-400 focus:outline-none py-2 max-h-32 resize-none text-sm sm:text-base ${colors.textMain}`} rows="1" />
          <button onClick={handleSend} disabled={!input.trim() || isSynthesizing} className={`p-2 shrink-0 rounded-lg transition-all ${input.trim() && !isSynthesizing ? 'bg-amber-500 text-white shadow-sm' : 'text-stone-300 bg-stone-100'}`}><Send className="w-4 h-4" /></button>
        </div>
      </div>
    </div>
  );
};

export default ChatView;
