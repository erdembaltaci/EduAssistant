'use client';
export const QuizScreen = ({ questions, userAnswers, onAnswerChange, onSubmit }) => (
  <div className="bg-white p-4 md:p-8 rounded-2xl shadow-lg animate-fade-in">
    <h2 className="text-2xl md:text-3xl font-bold mb-6 text-gray-800">Sınav Başladı</h2>
    {questions.map((q, index) => (
      <div key={index} className="mb-6 border-b pb-4 last:border-b-0">
        <p className="font-semibold text-base md:text-lg mb-4">{index + 1}. {q.question}</p>
        <div className="space-y-2">
          {q.options && Object.entries(q.options).map(([key, value]) => (
            <label key={key} className={`flex items-center p-3 rounded-lg border cursor-pointer transition-all ${userAnswers[index] === key ? 'bg-blue-100 border-blue-400' : 'border-gray-200 hover:bg-gray-50'}`}>
              <input type="radio" name={`question-${index}`} value={key} onChange={() => onAnswerChange(index, key)} className="w-4 h-4 mr-3 text-blue-600"/>
              <span><span className="font-semibold mr-2">{key})</span>{value}</span>
            </label>
          ))}
        </div>
      </div>
    ))}
    <div className="text-center mt-8">
      <button onClick={onSubmit} className="px-6 py-3 md:px-8 md:py-4 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700">Sınavı Bitir</button>
    </div>
  </div>
);