'use client';

import { useState, useEffect, useCallback } from 'react';
// Yeni bileşenlerimizi import ediyoruz
import { Header } from './components/Header';
import { InputPanel } from './components/InputPanel';
import { QuizScreen } from './components/QuizScreen';
import { ResultsScreen } from './components/ResultsScreen';
import { OutputDisplay } from './components/OutputDisplay';
import { HistoryPanel } from './components/HistoryPanel';

const SkeletonLoader = () => ( <div className="bg-white p-8 rounded-2xl shadow-lg w-full mt-10"><div className="animate-pulse"><div className="h-8 bg-gray-200 rounded-md w-3/4 mb-6"></div><div className="space-y-6">{[...Array(3)].map((_, i) => ( <div key={i} className="space-y-3"><div className="h-4 bg-gray-200 rounded-md w-5/6"></div><div className="h-4 bg-gray-200 rounded-md w-full"></div><div className="h-4 bg-gray-200 rounded-md w-4/6"></div></div> ))}</div></div></div> );

export default function Home() {
  const [mode, setMode] = useState('student');
  const [source, setSource] = useState('text');
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [questionType, setQuestionType] = useState('çoktan seçmeli');
  const [difficulty, setDifficulty] = useState('orta');
  const [quizStarted, setQuizStarted] = useState(false);
  const [userAnswers, setUserAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [copySuccess, setCopySuccess] = useState('');
  const [history, setHistory] = useState([]);

  const saveHistory = (newResult) => {
    try {
      const historyItem = { id: new Date().getTime(), type: newResult.summary ? 'Özet' : 'Sınav', topic: newResult.summary ? newResult.summary.substring(0, 40) + '...' : (newResult.questions && newResult.questions.length > 0) ? newResult.questions[0].question.substring(0, 40) + '...' : 'Oluşturulan İçerik', date: new Date().toLocaleString('tr-TR'), score: newResult.score };
      const currentHistory = JSON.parse(localStorage.getItem('pratikAiHistory')) || [];
      const updatedHistory = [historyItem, ...currentHistory].slice(0, 5);
      setHistory(updatedHistory);
      localStorage.setItem('pratikAiHistory', JSON.stringify(updatedHistory));
    } catch (error) { console.error("Geçmiş kaydedilirken hata oluştu:", error); }
  };
  
  const resetState = (keepMode = false) => {
    if (!keepMode) setMode('student');
    // setSource('text'); // Bu satırı bilinçli olarak kaldırdık.
    setText(''); setFile(null); setPreview(null);
    setResult(null); setError(''); setQuizStarted(false);
    setUserAnswers({}); setScore(null); setShowResults(false);
  };
  
  const handleModeChange = (newMode) => { setMode(newMode); resetState(true); };
  const handleSourceChange = (newSource) => { setSource(newSource); resetState(true); };
  
  const handleFileChange = (e) => { const selectedFile = e.target.files?.[0]; if (selectedFile) updateFile(selectedFile); };
  
  const handlePaste = useCallback((event) => {
    if (source !== 'file') return;
    const items = event.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const imageFile = items[i].getAsFile();
        if (imageFile) { updateFile(imageFile); event.preventDefault(); return; }
      }
    }
  }, [source]);

  const updateFile = (newFile) => {
    setFile(newFile);
    if (newFile.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(newFile);
    } else { setPreview(null); }
  };
  
  const handleSubmit = async () => {
    setIsLoading(true); setError(''); setResult(null); setQuizStarted(false);
    setUserAnswers({}); setScore(null); setShowResults(false);
    const formData = new FormData();
    let endpoint = '';
    if (source === 'text') {
        formData.append('text', text);
        endpoint = mode === 'summary' ? '/api/v1/generate-summary-from-text' : '/api/v1/generate-quiz-from-text';
    } else {
        if (!file) { setError('Lütfen bir dosya seçin veya yapıştırın.'); setIsLoading(false); return; }
        formData.append('file', file);
        endpoint = mode === 'summary' ? '/api/v1/generate-summary-from-file' : '/api/v1/generate-quiz-from-file';
    }
    if (mode === 'teacher') {
        formData.append('num_questions', numQuestions);
        formData.append('question_type', questionType);
        formData.append('difficulty', difficulty);
    } else if (mode === 'student') {
        formData.append('num_questions', 10);
        formData.append('question_type', 'çoktan seçmeli');
        formData.append('difficulty', 'orta');
    }
    try {
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, { method: 'POST', body: formData });
      if (!response.ok) {
          const errData = await response.json().catch(() => null);
          throw new Error(errData?.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setResult(data);
      if (mode !== 'student') { saveHistory(data); }
      if (mode === 'student' && data.questions && !data.questions[0]?.error) { setQuizStarted(true); }
    } catch (e) {
      console.error(e);
      setError(`İstek işlenirken bir hata oluştu: ${e.message}`);
    }
    setIsLoading(false);
  };
  
  const handleAnswerChange = (questionIndex, answerKey) => { setUserAnswers({ ...userAnswers, [questionIndex]: answerKey }); };

  const submitQuiz = () => {
      let correctCount = 0;
      result.questions.forEach((q, index) => { if (userAnswers[index] === q.correct_answer) correctCount++; });
      const finalScore = result.questions.length > 0 ? Math.round((correctCount / result.questions.length) * 100) : 0;
      setScore(finalScore);
      setShowResults(true);
      setQuizStarted(false);
      saveHistory({...result, score: finalScore });
  };

  const handlePdfDownload = async () => {
    if (!result || !result.questions) { setError('PDF oluşturulacak soru bulunamadı.'); return; }
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/download-quiz-pdf', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(result.questions) });
        if (!response.ok) throw new Error('PDF oluşturulamadı');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "PratikAi_Sinavi.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (err) { setError('PDF indirilirken bir hata oluştu.'); }
  };
  
  const handleCopyToClipboard = (textToCopy) => {
      navigator.clipboard.writeText(textToCopy).then(() => {
          setCopySuccess('Kopyalandı!');
          setTimeout(() => setCopySuccess(''), 2000);
      }, (err) => { console.error('Kopyalama hatası:', err); setError('Metin kopyalanamadı.'); });
  };

  useEffect(() => {
    window.addEventListener('paste', handlePaste);
    try {
      const savedHistory = JSON.parse(localStorage.getItem('pratikAiHistory')) || [];
      setHistory(savedHistory);
    } catch (error) { console.error("Geçmiş yüklenirken hata:", error); setHistory([]); }
    return () => window.removeEventListener('paste', handlePaste);
  }, [handlePaste]);

  const renderContent = () => {
    if (isLoading) return <SkeletonLoader />;
    if (quizStarted) return <QuizScreen questions={result.questions} userAnswers={userAnswers} onAnswerChange={handleAnswerChange} onSubmit={submitQuiz} />;
    if (showResults) return <ResultsScreen score={score} recommendations={result.recommendations} questions={result.questions} userAnswers={userAnswers} onNew={() => resetState(true)} onPdfDownload={handlePdfDownload} />;
    if (result) return <OutputDisplay result={result} mode={mode} copySuccess={copySuccess} onCopyToClipboard={handleCopyToClipboard} onPdfDownload={handlePdfDownload} onNew={() => resetState(true)} />;

    return (
      <InputPanel 
          states={{ mode, source, text, file, preview, isLoading, numQuestions, questionType, difficulty }}
          handlers={{ handleModeChange, handleSourceChange, setText, handleFileChange, setNumQuestions, setQuestionType, setDifficulty, handleSubmit }}
      />
    );
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-4 md:p-8 bg-gray-100 font-sans">
      <div className="w-full max-w-4xl">
        <Header />
        {error && <p className="text-center text-xl text-red-600 mb-4 animate-shake">{error}</p>}
        {renderContent()}
        
        {history.length > 0 && !quizStarted && !showResults && (
            <HistoryPanel history={history} />
        )}
      </div>
    </main>
  );
}