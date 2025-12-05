'use client';
const Recommendations = ({ recommendations }) => ( <div className="mt-8 border-t pt-6"><h3 className="text-2xl font-bold text-gray-800 mb-4">Bu Konuları Gözden Geçir</h3><div className="grid grid-cols-1 md:grid-cols-2 gap-4">{recommendations.map((rec, index) => ( <a key={index} href={rec.url} target="_blank" rel="noopener noreferrer" className="block p-4 bg-gray-50 rounded-lg hover:bg-blue-100 hover:shadow-md transition-all transform hover:-translate-y-1"><p className="font-semibold text-blue-600">{rec.title}</p></a> ))}</div></div> );
const SmartFeedback = ({ feedback }) => ( <div className="p-4 mt-6 mb-4 bg-yellow-50 border-l-4 border-yellow-400"><div className="flex"><div className="flex-shrink-0"><svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.21 3.03-1.742 3.03H4.42c-1.532 0-2.492-1.696-1.742-3.03l5.58-9.92zM10 13a1 1 0 110-2 1 1 0 010 2zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" /></svg></div><div className="ml-3"><p className="text-sm text-yellow-700"><span className="font-bold">Akıllı Geri Bildirim:</span> {feedback}</p></div></div></div> );

export const OutputDisplay = ({ result, mode, copySuccess, onCopyToClipboard, onPdfDownload, onNew }) => (
    <div className="bg-white p-4 md:p-8 rounded-2xl shadow-lg animate-fade-in-slow">
        <div className="flex flex-col md:flex-row justify-between items-center mb-4 gap-4">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-800">{result.summary ? 'Oluşturulan Özet' : 'Oluşturulan Sorular'}</h2>
            <div className="flex items-center space-x-2">
                {copySuccess && <span className="text-sm text-green-600 animate-pulse">{copySuccess}</span>}
                {result.summary && <button onClick={() => onCopyToClipboard(result.summary)} className="px-4 py-2 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300">Kopyala</button>}
                {result.questions && result.questions.length > 0 && !result.questions[0].error && ( <button onClick={onPdfDownload} className="px-4 py-2 bg-green-600 text-white font-semibold rounded-lg shadow-sm hover:bg-green-700">PDF İndir</button> )}
                <button onClick={onNew} className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-sm hover:bg-blue-700">Yeni İşlem Yap</button>
            </div>
        </div>
        {mode === 'teacher' && result.feedback && <SmartFeedback feedback={result.feedback} />}
        {result.summary && ( <div className="text-gray-700 whitespace-pre-wrap mt-4">{result.summary}</div> )}
        {result.questions && (
            <div className={mode === 'teacher' && result.feedback ? 'mt-4' : ''}>
                <h3 className="text-xl font-semibold mb-4 text-gray-700">Cevap Anahtarı</h3>
                {result.questions[0]?.raw_text ? (<p className="text-gray-700 whitespace-pre-wrap">{result.questions[0].raw_text}</p>) : 
                result.questions[0]?.error ? (<p className="text-red-600">{result.questions[0].error}</p>) :
                (result.questions.map((q, index) => (
                    <div key={index} className="mb-6 border-b pb-4 last:border-b-0">
                    <p className="font-semibold text-lg mb-2">{index + 1}. {q.question}</p>
                    {q.options && <ul className="space-y-1 pl-5">
                        {Object.entries(q.options).map(([key, value]) => ( <li key={key} className={`text-gray-700 ${q.correct_answer === key ? 'text-green-700 font-bold' : ''}`}><span className="font-semibold mr-2">{key})</span>{value}</li> ))}
                    </ul>}
                    </div>
                )))}
            </div>
        )}
            {result.recommendations && <Recommendations recommendations={result.recommendations} />}
    </div>
);