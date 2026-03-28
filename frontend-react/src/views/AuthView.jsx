import React, { useState } from 'react';
import { Command, Mail, Lock, User, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';
import { login, signup } from '../api';

const AuthView = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      if (isLogin) {
        await login(formData.username, formData.password);
      } else {
        await signup(formData.username, formData.email, formData.password);
      }
      onAuthSuccess();
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 relative overflow-hidden font-sans">
      {/* Background Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-amber-600/10 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-md z-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-amber-500 rounded-2xl shadow-xl shadow-amber-500/20 mb-6">
            <Command className="w-8 h-8 text-slate-900" />
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tight mb-2">Akasha</h1>
          <p className="text-slate-400 text-sm">The Sovereign Neural Library & Digital Ego</p>
        </div>

        <div className="bg-slate-900/50 backdrop-blur-2xl border border-slate-800 p-8 rounded-[32px] shadow-2xl">
          <div className="flex bg-slate-950/50 p-1.5 rounded-2xl mb-8 border border-slate-800">
            <button 
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2.5 rounded-xl text-sm font-bold transition-all ${isLogin ? 'bg-slate-800 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
            >
              Sign In
            </button>
            <button 
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2.5 rounded-xl text-sm font-bold transition-all ${!isLogin ? 'bg-slate-800 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
            >
              Initialize
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-[10px] uppercase font-bold text-slate-500 mb-2 tracking-widest">Username</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input 
                  type="text" 
                  name="username"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full bg-slate-950 border border-slate-800 rounded-2xl py-3.5 pl-12 pr-4 text-white text-sm focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/50 outline-none transition-all"
                  placeholder="archivist_01"
                />
              </div>
            </div>

            {!isLogin && (
              <div>
                <label className="block text-[10px] uppercase font-bold text-slate-500 mb-2 tracking-widest">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input 
                    type="email" 
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl py-3.5 pl-12 pr-4 text-white text-sm focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/50 outline-none transition-all"
                    placeholder="you@sovereign.net"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-[10px] uppercase font-bold text-slate-500 mb-2 tracking-widest">Neural Key</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input 
                  type="password" 
                  name="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full bg-slate-950 border border-slate-800 rounded-2xl py-3.5 pl-12 pr-4 text-white text-sm focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/50 outline-none transition-all"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-500 text-xs font-medium animate-shake">
                {error}
              </div>
            )}

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold py-4 rounded-2xl flex items-center justify-center transition-all shadow-lg shadow-amber-500/10 active:scale-[0.98] disabled:opacity-50"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-slate-900 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  {isLogin ? 'Access Neural Core' : 'Initialize Personal Pod'}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-8 border-t border-slate-800 flex items-center justify-between">
            <div className="flex items-center text-[10px] text-slate-500 font-bold tracking-widest uppercase">
              <ShieldCheck className="w-3.5 h-3.5 mr-1.5 text-green-500" />
              Sovereign Auth
            </div>
            <div className="flex items-center text-[10px] text-slate-500 font-bold tracking-widest uppercase">
              <Sparkles className="w-3.5 h-3.5 mr-1.5 text-blue-500" />
              Zero-Trust
            </div>
          </div>
        </div>
        
        <p className="mt-8 text-center text-slate-600 text-xs italic">
          "Your data is your mirror. No one else should see the reflection."
        </p>
      </div>
    </div>
  );
};

export default AuthView;
