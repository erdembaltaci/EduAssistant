'use client';
const Spinner = () => ( <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> );

export const InputPanel = ({ states, handlers }) => {
  const { mode, source, text, file, preview, isLoading, numQuestions, questionType, difficulty } = states;
  const { handleModeChange, handleSourceChange, setText, handleFileChange, setNumQuestions, setQuestionType, setDifficulty, handleSubmit } = handlers;

  return (
    <div>
      <div className="flex justify-center space-x-2 mb-8 p-1 bg-gray-200 rounded-xl">
        <button onClick={() => handleModeChange('student')} className={`px-6 py-2 rounded-lg font-semibold transition-colors ${mode === 'student' ? 'bg-white text-blue-600 shadow' : 'text-gray-600'}`}>Öğrenci</button>
        <button onClick={() => handleModeChange('teacher')} className={`px-6 py-2 rounded-lg font-semibold transition-colors ${mode === 'teacher' ? 'bg-white text-blue-600 shadow' : 'text-gray-600'}`}>Öğretmen</button>
        <button onClick={() => handleModeChange('summary')} className={`px-6 py-2 rounded-lg font-semibold transition-colors ${mode === 'summary' ? 'bg-white text-blue-600 shadow' : 'text-gray-600'}`}>Özet Çıkar</button>
      </div>
      <div className="bg-white p-4 md:p-8 rounded-2xl shadow-lg">
        <div className="flex items-center space-x-4 mb-6">
            <label className="font-semibold text-gray-700">Kaynak Türü:</label>
            <button onClick={() => handleSourceChange('text')} className={`px-4 py-1 rounded-full text-sm ${source === 'text' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}>Metin</button>
            <button onClick={() => handleSourceChange('file')} className={`px-4 py-1 rounded-full text-sm ${source === 'file' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}>Dosya / Görsel</button>
        </div>
        {source === 'text' ? (
            <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Metni buraya yapıştırın..." className="w-full h-40 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"></textarea>
        ) : (
            <div>
                <label htmlFor="file-upload" className="relative block w-full h-52 border-2 border-dashed border-gray-300 rounded-lg flex justify-center items-center text-center cursor-pointer hover:border-blue-500">
                    {preview ? <img src={preview} alt="Önizleme" className="max-h-full max-w-full object-contain" /> : file ? <p>{file.name}</p> : <div className="text-gray-500"><p>Ekran görüntüsü yapıştırın (CTRL+V)</p><p className="my-1">veya</p><p className="font-semibold text-blue-600">tıklayın</p></div>}
                </label>
                <input id="file-upload" type="file" className="sr-only" onChange={handleFileChange} accept="image/*,application/pdf" />
            </div>
        )}
        <div className={`grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 border-t pt-6 ${mode !== 'teacher' ? 'hidden' : ''}`}>
            <div><label className="block text-sm font-medium text-gray-700 mb-1">Soru Sayısı</label><input type="number" value={numQuestions} onChange={(e) => setNumQuestions(e.target.value)} min="1" max="10" className="w-full p-2 border border-gray-300 rounded-md" /></div>
            <div><label className="block text-sm font-medium text-gray-700 mb-1">Soru Tipi</label><select value={questionType} onChange={(e) => setQuestionType(e.target.value)} className="w-full p-2 border border-gray-300 rounded-md"><option value="çoktan seçmeli">Çoktan Seçmeli</option><option value="doğru-yanlış">Doğru/Yanlış</option><option value="boşluk doldurma">Boşluk Doldurma</option></select></div>
            <div><label className="block text-sm font-medium text-gray-700 mb-1">Zorluk</label><select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="w-full p-2 border border-gray-300 rounded-md"><option value="kolay">Kolay</option><option value="orta">Orta</option><option value="zor">Zor</option></select></div>
        </div>
        <div className="mt-6 text-center">
            <button onClick={handleSubmit} disabled={isLoading || (source === 'text' && !text.trim()) || (source === 'file' && !file)} className="inline-flex items-center px-6 py-3 md:px-8 md:py-4 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400">
            {isLoading && <Spinner />}
            {isLoading ? 'Oluşturuluyor...' : (mode === 'summary' ? 'Özet Çıkar' : 'Sınav Oluştur')}
            </button>
        </div>
      </div>
    </div>
  );
};