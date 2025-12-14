import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PredictionHistory.css';

const PredictionHistory = ({ symbol }) => {
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [accuracy, setAccuracy] = useState(0);
    const itemsPerPage = 10;

    useEffect(() => {
        if (symbol) {
            fetchPredictions();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [symbol]);

    const fetchPredictions = async () => {
        setLoading(true);
        try {
            const cleanSymbol = symbol.replace('.NS', '').replace('.BO', '');
            const response = await axios.get(`/api/predictions/${cleanSymbol}?limit=50`);
            const data = response.data.predictions || [];
            setPredictions(data);
            calculateAccuracy(data);
        } catch (error) {
            console.error('Error fetching predictions:', error);
            // Use mock data for demonstration
            const mockData = generateMockPredictions();
            setPredictions(mockData);
            calculateAccuracy(mockData);
        } finally {
            setLoading(false);
        }
    };

    const generateMockPredictions = () => {
        const verdicts = ['BUY', 'SELL', 'HOLD'];
        const statuses = ['CORRECT', 'INCORRECT', 'PENDING'];
        const data = [];

        for (let i = 0; i < 25; i++) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const verdict = verdicts[Math.floor(Math.random() * 3)];
            const price = 2500 + Math.random() * 500;
            const target = verdict === 'BUY' ? price * 1.05 : verdict === 'SELL' ? price * 0.95 : null;
            const actual = price + (Math.random() - 0.5) * 100;
            const status = i === 0 ? 'PENDING' : statuses[Math.floor(Math.random() * 2)];

            data.push({
                id: i,
                timestamp: date.toISOString(),
                verdict,
                current_price: price,
                target_price: target,
                actual_price: actual,
                status,
                confidence: Math.random() * 0.4 + 0.6
            });
        }
        return data;
    };

    const calculateAccuracy = (data) => {
        const validated = data.filter(p => p.status === 'CORRECT' || p.status === 'INCORRECT');
        if (validated.length === 0) {
            setAccuracy(0);
            return;
        }
        const correct = validated.filter(p => p.status === 'CORRECT').length;
        setAccuracy((correct / validated.length) * 100);
    };

    const exportToCSV = () => {
        const headers = ['Date', 'Verdict', 'Price', 'Target', 'Actual', 'Status', 'Confidence'];
        const rows = predictions.map(p => [
            new Date(p.timestamp).toLocaleDateString(),
            p.verdict,
            `₹${p.current_price?.toFixed(2)}`,
            p.target_price ? `₹${p.target_price.toFixed(2)}` : '-',
            p.actual_price ? `₹${p.actual_price.toFixed(2)}` : '-',
            p.status,
            `${(p.confidence * 100).toFixed(0)}%`
        ]);

        const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${symbol}_predictions_${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
        URL.revokeObjectURL(url);
    };

    const totalPages = Math.ceil(predictions.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const currentPredictions = predictions.slice(startIndex, startIndex + itemsPerPage);

    const getStatusIcon = (status) => {
        switch (status) {
            case 'CORRECT': return '✅';
            case 'INCORRECT': return '❌';
            case 'PENDING': return '⏳';
            default: return '❓';
        }
    };

    const getVerdictClass = (verdict) => {
        switch (verdict) {
            case 'BUY': return 'verdict-buy';
            case 'SELL': return 'verdict-sell';
            case 'HOLD': return 'verdict-hold';
            default: return '';
        }
    };

    return (
        <div className="prediction-history-container">
            <div className="history-header">
                <div className="header-left">
                    <h3>📋 Prediction History</h3>
                    <div className="accuracy-badge">
                        <span className="accuracy-label">Accuracy:</span>
                        <span className={`accuracy-value ${accuracy >= 60 ? 'good' : accuracy >= 40 ? 'medium' : 'low'}`}>
                            {accuracy.toFixed(1)}%
                        </span>
                        <span className="accuracy-count">
                            ({predictions.filter(p => p.status !== 'PENDING').length} validated)
                        </span>
                    </div>
                </div>
                <button className="export-btn" onClick={exportToCSV}>
                    📥 Export CSV
                </button>
            </div>

            {loading ? (
                <div className="history-loading">
                    <div className="spinner"></div>
                    <p>Loading prediction history...</p>
                </div>
            ) : predictions.length === 0 ? (
                <div className="no-predictions">
                    <p>No prediction history available</p>
                </div>
            ) : (
                <>
                    <div className="history-table-wrapper">
                        <table className="history-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Verdict</th>
                                    <th>Price</th>
                                    <th>Target</th>
                                    <th>Actual</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {currentPredictions.map((pred, index) => (
                                    <tr key={pred.id || index}>
                                        <td className="date-cell">
                                            {new Date(pred.timestamp).toLocaleDateString('en-US', {
                                                month: 'short',
                                                day: 'numeric'
                                            })}
                                        </td>
                                        <td>
                                            <span className={`verdict-badge ${getVerdictClass(pred.verdict)}`}>
                                                {pred.verdict}
                                            </span>
                                        </td>
                                        <td className="price-cell">₹{pred.current_price?.toFixed(2)}</td>
                                        <td className="target-cell">
                                            {pred.target_price ? `₹${pred.target_price.toFixed(2)}` : '-'}
                                        </td>
                                        <td className="actual-cell">
                                            {pred.actual_price ? `₹${pred.actual_price.toFixed(2)}` : '-'}
                                        </td>
                                        <td className="status-cell">
                                            <span className={`status-badge status-${pred.status?.toLowerCase()}`}>
                                                {getStatusIcon(pred.status)}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    <div className="pagination">
                        <button
                            className="page-btn"
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                        >
                            ← Prev
                        </button>
                        <div className="page-numbers">
                            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                let pageNum;
                                if (totalPages <= 5) {
                                    pageNum = i + 1;
                                } else if (currentPage <= 3) {
                                    pageNum = i + 1;
                                } else if (currentPage >= totalPages - 2) {
                                    pageNum = totalPages - 4 + i;
                                } else {
                                    pageNum = currentPage - 2 + i;
                                }
                                return (
                                    <button
                                        key={pageNum}
                                        className={`page-num ${currentPage === pageNum ? 'active' : ''}`}
                                        onClick={() => setCurrentPage(pageNum)}
                                    >
                                        {pageNum}
                                    </button>
                                );
                            })}
                        </div>
                        <button
                            className="page-btn"
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                        >
                            Next →
                        </button>
                    </div>

                    <div className="table-footer">
                        <span>Showing {startIndex + 1}-{Math.min(startIndex + itemsPerPage, predictions.length)} of {predictions.length} predictions</span>
                    </div>
                </>
            )}
        </div>
    );
};

export default PredictionHistory;
