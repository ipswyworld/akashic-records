import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, Trash2, CheckCircle, Circle, Calendar, Tag, 
  AlertCircle, Sparkles, Brain, Clock, ChevronDown, ChevronUp, 
  Lightbulb, Layers, Zap, Info
} from 'lucide-react';
import { 
  fetchTodos, createTodo, updateTodo, deleteTodo, 
  strategizeTodo, decomposeTodo, harvestTodos 
} from '../api';

const TodoView = () => {
  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState('');
  const [category, setCategory] = useState('general');
  const [dueDate, setDueDate] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [error, setError] = useState(null);
  const [egoFeedback, setEgoFeedback] = useState(null);
  const [strategies, setStrategies] = useState({});
  const [isStrategizing, setIsStrategizing] = useState({});
  const [harvestedSuggestions, setHarvestedSuggestions] = useState([]);
  const [isHarvesting, setIsHarvesting] = useState(false);
  const [filter, setFilter] = useState('active'); // active, completed, urgent, all

  useEffect(() => {
    loadTodos();
  }, []);

  const loadTodos = async () => {
    try {
      const data = await fetchTodos();
      // Sort: Urgent first, then by due date
      const sorted = data.sort((a, b) => {
        if (a.completed !== b.completed) return a.completed ? 1 : -1;
        if (a.due_date && b.due_date) return new Date(a.due_date) - new Date(b.due_date);
        if (a.due_date) return -1;
        if (b.due_date) return 1;
        return (b.urgency_score || 0) - (a.urgency_score || 0);
      });
      setTodos(sorted);
    } catch (err) {
      console.error("Failed to load todos:", err);
      setError("Could not connect to the neural core.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddTodo = async (e, textOverride = null) => {
    if (e) e.preventDefault();
    const textToAdd = textOverride || newTodo;
    if (!textToAdd.trim() || isAdding) return;

    // Optimistic Update
    const tempId = 'temp-' + Date.now();
    const optimisticTodo = {
      id: tempId,
      text: textToAdd,
      category,
      due_date: dueDate || null,
      completed: false,
      created_at: new Date().toISOString()
    };
    setTodos([optimisticTodo, ...todos]);
    if (!textOverride) {
      setNewTodo('');
      setDueDate('');
    }

    setIsAdding(true);
    setError(null);
    setEgoFeedback(null);
    try {
      const result = await createTodo({ text: textToAdd, category, due_date: dueDate || null });
      // Replace optimistic todo with real one
      setTodos(prev => prev.map(t => t.id === tempId ? result.todo : t));
      setEgoFeedback(result.ego_feedback);
      
      if (textOverride) {
        setHarvestedSuggestions(prev => prev.filter(s => s.text !== textOverride));
      }

      setTimeout(() => setEgoFeedback(null), 10000);
    } catch (err) {
      // Rollback
      setTodos(prev => prev.filter(t => t.id !== tempId));
      setError("Failed to sync intention. The digital ego is currently offline.");
    } finally {
      setIsAdding(false);
    }
  };

  const handleToggleTodo = async (todo) => {
    // Optimistic Update
    const originalTodos = [...todos];
    setTodos(todos.map(t => t.id === todo.id ? { ...t, completed: !t.completed } : t));
    
    try {
      const updated = await updateTodo(todo.id, { completed: !todo.completed });
      setTodos(prev => prev.map(t => t.id === todo.id ? updated : t));
    } catch (err) {
      setTodos(originalTodos);
      setError("Failed to sync completion state.");
    }
  };

  const handleDeleteTodo = async (id) => {
    try {
      await deleteTodo(id);
      setTodos(todos.filter(t => t.id !== id && t.parent_id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleStrategize = async (id) => {
    if (isStrategizing[id]) return;
    setIsStrategizing(prev => ({ ...prev, [id]: true }));
    try {
      const result = await strategizeTodo(id);
      setStrategies(prev => ({ ...prev, [id]: result.strategy }));
    } catch (err) {
      console.error(err);
    } finally {
      setIsStrategizing(prev => ({ ...prev, [id]: false }));
    }
  };

  const handleDecompose = async (id) => {
    setIsStrategizing(prev => ({ ...prev, [id]: true }));
    try {
      const newSteps = await decomposeTodo(id);
      setTodos([...todos, ...newSteps]);
    } catch (err) {
      console.error(err);
    } finally {
      setIsStrategizing(prev => ({ ...prev, [id]: false }));
    }
  };

  const handleHarvest = async () => {
    setIsHarvesting(true);
    try {
      const suggestions = await harvestTodos();
      setHarvestedSuggestions(suggestions);
    } catch (err) {
      console.error(err);
    } finally {
      setIsHarvesting(false);
    }
  };

  const safeFormatDate = (dateStr) => {
    if (!dateStr) return null;
    // Replace space with T for ISO compatibility if needed
    const isoStr = typeof dateStr === 'string' && dateStr.includes(' ') ? dateStr.replace(' ', 'T') : dateStr;
    const d = new Date(isoStr);
    return isNaN(d.getTime()) ? null : d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  // Organize into hierarchy and filter
  const filteredTodos = todos.filter(t => {
    if (filter === 'active') return !t.completed;
    if (filter === 'completed') return t.completed;
    if (filter === 'urgent') return !t.completed && (t.due_date || t.urgency_score > 0.7);
    return true;
  });

  const parentTodos = filteredTodos.filter(t => !t.parent_id);
  const getSubTasks = (parentId) => filteredTodos.filter(t => t.parent_id === parentId);

  const completedCount = todos.filter(t => t.completed).length;
  const progress = todos.length > 0 ? (completedCount / todos.length) * 100 : 0;

  return (
    <div className="flex flex-col h-full bg-stone-50 p-6 overflow-hidden">
      <header className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-serif text-stone-800">Neural Intentions</h1>
          <p className="text-stone-500 font-sans italic">"The shortest path to the self is through action."</p>
        </div>
        
        <div className="flex flex-col items-end gap-3">
          <button 
            onClick={handleHarvest}
            disabled={isHarvesting}
            className="flex items-center gap-2 px-4 py-2 bg-stone-800 text-stone-100 rounded-xl hover:bg-stone-700 transition-all text-sm shadow-md"
          >
            {isHarvesting ? <Zap className="w-4 h-4 animate-spin" /> : <Layers className="w-4 h-4 text-amber-400" />}
            Neural Harvest
          </button>

          <AnimatePresence>
            {egoFeedback && (
              <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="max-w-xs bg-amber-50 border border-amber-200 p-3 rounded-xl shadow-sm flex gap-3 items-start"
              >
                <Brain className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                <div className="text-sm text-stone-700 italic">"{egoFeedback}"</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-[10px] font-bold text-stone-400 uppercase tracking-widest mb-1">
          <span>Intention Realization</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="h-1.5 w-full bg-stone-200 rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            className="h-full bg-amber-500"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {['active', 'urgent', 'completed', 'all'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider transition-all ${filter === f ? 'bg-amber-500 text-white shadow-md' : 'bg-white text-stone-400 hover:bg-stone-100'}`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Harvested Suggestions */}
      <AnimatePresence>
        {harvestedSuggestions.length > 0 && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="mb-6 overflow-hidden"
          >
            <div className="bg-stone-100 border border-stone-200 p-4 rounded-2xl">
              <div className="flex items-center gap-2 text-stone-500 text-xs font-bold uppercase tracking-widest mb-3">
                <Sparkles className="w-3 h-3 text-amber-500" />
                Implied Intentions from Library
              </div>
              <div className="flex flex-wrap gap-2">
                {harvestedSuggestions.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => handleAddTodo(null, s.text)}
                    className="bg-white border border-stone-200 px-3 py-1.5 rounded-lg text-sm text-stone-700 hover:border-amber-300 hover:bg-amber-50 transition-all flex items-center gap-2"
                  >
                    <Plus className="w-3 h-3 text-amber-500" />
                    {s.text}
                  </button>
                ))}
                <button 
                  onClick={() => setHarvestedSuggestions([])}
                  className="text-stone-400 text-xs hover:text-stone-600 px-2"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <form onSubmit={handleAddTodo} className="mb-8 flex flex-wrap gap-2">
        <div className="flex-1 min-w-[200px] relative">
          <input
            type="text"
            value={newTodo}
            onChange={(e) => setNewTodo(e.target.value)}
            placeholder="Commit to a new intention..."
            className="w-full bg-white border border-stone-200 rounded-xl py-3 px-4 focus:ring-2 focus:ring-amber-200 outline-none transition-all shadow-sm"
          />
        </div>
        <div className="flex gap-2">
          <input
            type="datetime-local"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="bg-white border border-stone-200 rounded-xl px-3 text-stone-600 outline-none shadow-sm font-sans text-xs"
          />
          <select 
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="bg-white border border-stone-200 rounded-xl px-3 text-stone-600 outline-none shadow-sm font-sans text-xs"
          >
            <option value="general">General</option>
            <option value="work">Work</option>
            <option value="personal">Personal</option>
            <option value="health">Health</option>
            <option value="learning">Learning</option>
          </select>
          <button 
            type="submit"
            disabled={isAdding}
            className={`${isAdding ? 'bg-amber-300' : 'bg-amber-500 hover:bg-amber-600'} text-white rounded-xl px-6 py-2 transition-all shadow-md flex items-center gap-2 font-bold`}
          >
            {isAdding ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div> : <Plus className="w-5 h-5" />}
            Add
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-100 text-red-600 rounded-xl flex items-center gap-2 text-sm">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      <div className="flex-1 overflow-y-auto custom-scrollbar px-1">
        {isLoading ? (
          <div className="flex justify-center py-10"><Zap className="w-8 h-8 text-amber-200 animate-pulse" /></div>
        ) : (
          <div className="space-y-6">
            <AnimatePresence>
              {parentTodos.map((todo) => (
                <div key={todo.id} className="space-y-2">
                  <TodoItem 
                    todo={todo} 
                    onToggle={handleToggleTodo} 
                    onDelete={handleDeleteTodo}
                    onStrategize={handleStrategize}
                    onDecompose={handleDecompose}
                    strategy={strategies[todo.id]}
                    isBusy={isStrategizing[todo.id]}
                    formatDate={safeFormatDate}
                  />
                  
                  {/* Sub-tasks */}
                  <div className="ml-10 space-y-2">
                    {getSubTasks(todo.id).map(sub => (
                      <TodoItem 
                        key={sub.id} 
                        todo={sub} 
                        isSub={true}
                        onToggle={handleToggleTodo} 
                        onDelete={handleDeleteTodo}
                        formatDate={safeFormatDate}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </AnimatePresence>
            
            {parentTodos.length === 0 && (
              <div className="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-stone-200">
                <p className="text-stone-400 font-serif text-lg">Your intentions are silent. The library awaits your focus.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const TodoItem = ({ todo, isSub, onToggle, onDelete, onStrategize, onDecompose, strategy, isBusy, formatDate }) => {
  const isUrgent = todo.due_date || (todo.urgency_score > 0.7);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className={`flex flex-col bg-white rounded-2xl border ${isSub ? 'border-stone-100 shadow-none' : 'border-stone-200 shadow-sm'} transition-all overflow-hidden ${todo.completed ? 'opacity-50' : ''} ${!todo.completed && isUrgent && !isSub ? 'border-l-4 border-l-amber-500' : ''}`}
    >
      <div className="flex items-center gap-4 p-4">
        <button 
          onClick={() => onToggle(todo)}
          className="text-amber-500 hover:scale-110 transition-transform"
        >
          {todo.completed ? <CheckCircle className="w-6 h-6" /> : <Circle className="w-6 h-6" />}
        </button>
        
        <div className="flex-1">
          <p className={`text-stone-800 ${isSub ? 'text-sm' : 'font-medium'} ${todo.completed ? 'line-through' : ''}`}>
            {todo.text}
          </p>
          <div className="flex gap-3 mt-1 text-[9px] text-stone-400 uppercase tracking-widest font-bold">
            <span className="flex items-center gap-1"><Tag className="w-3 h-3" />{todo.category}</span>
            {!isSub && <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{formatDate(todo.created_at)}</span>}
            {!todo.completed && todo.due_date && <span className="flex items-center gap-1 text-red-400"><Calendar className="w-3 h-3" />Due: {formatDate(todo.due_date)}</span>}
          </div>
        </div>

        <div className="flex items-center gap-1">
          {!todo.completed && !isSub && (
            <>
              <button 
                onClick={() => onDecompose(todo.id)}
                className="p-2 text-stone-300 hover:text-amber-500 hover:bg-amber-50 rounded-xl transition-all"
                title="Decompose (Breakdown)"
              >
                <Layers className={`w-4 h-4 ${isBusy ? 'animate-pulse' : ''}`} />
              </button>
              <button 
                onClick={() => onStrategize(todo.id)}
                className={`p-2 rounded-xl transition-all ${strategy ? 'bg-amber-100 text-amber-600' : 'text-stone-300 hover:bg-stone-100 hover:text-amber-500'}`}
                title="Neural Strategy"
              >
                <Sparkles className={`w-4 h-4 ${isBusy ? 'animate-pulse' : ''}`} />
              </button>
            </>
          )}
          
          <button 
            onClick={() => onDelete(todo.id)}
            className="p-2 text-stone-200 hover:text-red-400 hover:bg-red-50 rounded-xl transition-all"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {strategy && (
        <motion.div 
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          className="bg-amber-50/50 border-t border-amber-100 px-4 py-3 flex gap-3"
        >
          <Lightbulb className="w-4 h-4 text-amber-500 shrink-0 mt-1" />
          <p className="text-sm text-stone-600 leading-relaxed italic">
            {strategy}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default TodoView;
