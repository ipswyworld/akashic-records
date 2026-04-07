import React, { useState, useEffect } from 'react';
import { 
  GraduationCap, BookOpen, Brain, Sparkles, 
  CheckCircle2, ChevronRight, Play, Trophy,
  RotateCcw, HelpCircle, Lightbulb
} from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';
import gsap from 'gsap';

const TutorView = ({ theme }) => {
  const [syllabus, setSyllabus] = useState(null);
  const [quiz, setQuiz] = useState([]);
  const [activeQuestion, setActiveQuestion] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [userScore, setUserScore] = useState(0);
  const [showResults, setShowScore] = useState(false);
  const colors = getThemeColors(theme);

  const startLearningPath = async () => {
    setIsLoading(true);
    // In a real implementation, we'd select artifact IDs based on recent interest
    try {
      const res = await fetch('http://localhost:8001/tutor/syllabus', {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${localStorage.getItem('akasha_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify([]) // Backend will fallback to random artifacts
      });
      const data = await res.json();
      setSyllabus(data);
    } catch (err) { console.error(err); }
    finally { setIsLoading(false); }
  };

  useEffect(() => {
    gsap.from('.tutor-anim', { y: 20, opacity: 0, duration: 0.8, stagger: 0.1 });
  }, []);

  return (
    <div className="p-6 sm:p-10 max-w-5xl mx-auto w-full min-h-screen">
      <div className="flex justify-between items-start mb-12">
        <div>
          <h1 className={`text-4xl font-bold mb-2 flex items-center gap-4 ${colors.textMain}`}>
            <GraduationCap className="w-10 h-10 text-amber-500" /> Synaptic Tutor
          </h1>
          <p className="text-stone-500 font-mono text-xs uppercase tracking-widest">Active Accelerated Learning Engine</p>
        </div>
        {!syllabus && (
          <button 
            onClick={startLearningPath}
            className="px-8 py-3 bg-amber-500 text-slate-900 font-black rounded-2xl shadow-xl shadow-amber-500/20 hover:scale-105 transition-all uppercase tracking-widest text-xs"
          >
            Generate Learning Path
          </button>
        )}
      </div>

      {!syllabus ? (
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-6 tutor-anim">
          <div className="p-10 rounded-[40px] bg-stone-100/50 border-2 border-dashed border-stone-200">
            <Brain className="w-16 h-16 text-stone-300 mx-auto mb-6" />
            <h3 className="text-xl font-bold text-stone-400">Your Neural Pathways are Idle</h3>
            <p className="text-sm text-stone-500 max-w-sm mx-auto mt-2">
              Akasha can synthesize your ingested research into a custom university-level syllabus.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 tutor-anim">
          {/* Syllabus Section */}
          <div className="lg:col-span-2 space-y-8">
            <div className={`p-8 rounded-[40px] border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
              <h3 className="text-xs font-black text-amber-600 uppercase tracking-[0.3em] mb-8 flex items-center">
                <BookOpen className="w-4 h-4 mr-2" /> Current Syllabus: {syllabus.topic}
              </h3>
              <div className="space-y-6">
                {syllabus.steps.map((step, i) => (
                  <div key={i} className="group flex gap-6 p-6 rounded-3xl hover:bg-stone-50 transition-all border border-transparent hover:border-stone-100">
                    <div className="flex flex-col items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-mono text-xs font-bold ${i === 0 ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/30' : 'bg-stone-100 text-stone-400'}`}>
                        {i + 1}
                      </div>
                      {i < syllabus.steps.length - 1 && <div className="w-0.5 flex-1 bg-stone-100 my-2"></div>}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-bold text-stone-800">{step.title}</h4>
                      <p className="text-sm text-stone-500 mt-1 leading-relaxed">{step.concept}</p>
                      <button className="mt-4 flex items-center gap-2 text-[10px] font-black text-amber-600 uppercase tracking-widest hover:translate-x-1 transition-transform">
                        Launch Lesson <ChevronRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Stats & Tools */}
          <div className="space-y-8">
            <div className={`p-8 rounded-[40px] border shadow-sm ${colors.panel} ${colors.panelBorder}`}>
              <h3 className="text-xs font-black text-blue-500 uppercase tracking-[0.3em] mb-6 flex items-center">
                <Trophy className="w-4 h-4 mr-2" /> Mastery Rank
              </h3>
              <div className="text-center py-4">
                <div className="text-5xl font-black text-slate-900 mb-2">Novice</div>
                <p className="text-[10px] text-stone-400 uppercase tracking-widest font-bold">Progress: 12% to Apprentice</p>
                <div className="w-full h-1.5 bg-stone-100 rounded-full mt-6 overflow-hidden">
                  <div className="h-full bg-blue-500 w-[12%]" />
                </div>
              </div>
            </div>

            <div className={`p-8 rounded-[40px] border shadow-sm bg-slate-900 text-white`}>
              <h3 className="text-xs font-black text-amber-500 uppercase tracking-[0.3em] mb-6 flex items-center">
                <Sparkles className="w-4 h-4 mr-2" /> Quick Quiz
              </h3>
              <p className="text-sm text-slate-400 mb-8 leading-relaxed">
                Test your retention of today's research artifacts.
              </p>
              <button className="w-full py-4 bg-amber-500 text-slate-900 font-black rounded-2xl shadow-xl shadow-amber-500/20 hover:bg-amber-400 transition-all uppercase tracking-widest text-[10px]">
                Enter Exam Mode
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TutorView;
