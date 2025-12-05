'use client';

export const HistoryPanel = ({ history }) => (
    <div className="mt-10 w-full">
        <div className="bg-white p-8 rounded-2xl shadow-lg">
            <h2 className="text-2xl font-bold mb-4 text-gray-700">Son İşlemlerim</h2>
            <ul className="space-y-3">
                {history.map((item) => (
                    <li key={item.id} className="p-3 bg-gray-50 rounded-md flex justify-between items-center">
                        <div>
                            <span className={`font-semibold ${item.type === 'Sınav' ? 'text-blue-600' : 'text-purple-600'}`}>{item.type}</span>
                            <span className="text-gray-600 mx-2">-</span>
                            <span className="text-gray-800">{item.topic}</span>
                            {item.score !== undefined && <span className={`ml-2 font-bold text-lg ${item.score >= 70 ? 'text-green-600' : 'text-red-600'}`}>{item.score}</span>}
                        </div>
                        <span className="text-sm text-gray-400">{item.date}</span>
                    </li>
                ))}
            </ul>
        </div>
    </div>
);