'use client';
const Recommendations = ({ recommendations }) => ( <div className="mt-8 border-t pt-6"><h3 className="text-2xl font-bold text-gray-800 mb-4">Bu Konuları Gözden Geçir</h3><div className="grid grid-cols-1 md:grid-cols-2 gap-4">{recommendations.map((rec, index) => ( <a key={index} href={rec.url} target="_blank" rel="noopener noreferrer" className="block p-4 bg-gray-50 rounded-lg hover:bg-blue-100 hover:shadow-md transition-all transform hover:-translate-y-1"><p className="font-semibold text-blue-600">{rec.title}</p></a> ))}</div></div> );

export const ResultsScreen = ({ score, recommendations, questions, userAnswers, onNew, onPdfDownload }) => (
  <div className="bg-white p-4 md:p-8 rounded-2xl shadow-lg animate-fade-in-slow">
    <div className="text-center border-b pb-6 mb-6">
      <h2 className="text-2xl md:text-3xl font-bold mb-2 text-gray-800">Sınav Sonucu</h2>
      <p className={`text-5xl md:text-6xl font-extrabold ${score >= 70 ? 'text-green-600' : 'text-red-600'}`}>{score}</p>
      <p className="font-semibold mt-2">{score >= 70 ? "Tebrikler!" : "Biraz daha tekrar iyi olabilir!"}</p>
    </div>
    {score < 70 && recommendations && <Recommendations recommendations={recommendations} />}
    <div className="flex flex-col md:flex-row justify-between items-center my-4 gap-4">
      <button onClick={onNew} className="w-full md:w-auto px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-sm hover:bg-blue-700">Yeni İşlem Yap</button>
      <button onClick={onPdfDownload} className="w-full md:w-auto px-4 py-2 bg-gray-600 text-white font-semibold rounded-lg shadow-sm hover:bg-gray-700">Cevap Anahtarını PDF İndir</button>
    </div>
    {questions.map((q, index) => (
      <div key={index} className="mb-6 border-b pb-4 last:border-b-0">
        <p className="font-semibold text-base md:text-lg mb-2">{index + 1}. {q.question}</p>
        <ul className="space-y-1 pl-5">
          {q.options && Object.entries(q.options).map(([key, value]) => {
            const isCorrect = q.correct_answer === key;
            const isUserChoice = userAnswers[index] === key;
            let style = 'text-gray-700 text-sm md:text-base';
            if (isCorrect) style = 'text-green-700 font-bold text-sm md:text-base';
            if (!isCorrect && isUserChoice) style = 'text-red-700 line-through text-sm md:text-base';
            return ( <li key={key} className={style}><span className="font-semibold mr-2">{key})</span>{value}{isCorrect && ' ✔️'}{isUserChoice && !isCorrect && ' ❌'}</li> )
          })}
        </ul>
      </div>
    ))}
  </div>
);