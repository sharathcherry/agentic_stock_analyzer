import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Custom hook for fetching and managing technical indicators.
 * Provides RSI, MACD, SMA, Bollinger Bands data.
 * 
 * @param {string} ticker - Stock ticker symbol (e.g., 'RELIANCE.NS')
 * @returns {object} Technical indicators, loading state, error, and refresh function
 */
export const useTechnicals = (ticker) => {
    const [indicators, setIndicators] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);

    const fetchIndicators = useCallback(async () => {
        if (!ticker) return;

        setLoading(true);
        setError(null);

        try {
            const response = await axios.get(`${API_BASE}/api/stock/${ticker}/technical`);

            // Process and normalize indicator data
            const data = response.data.indicators || {};

            const normalizedIndicators = {
                rsi: {
                    value: data.rsi?.value || null,
                    signal: getSignalFromRSI(data.rsi?.value),
                    interpretation: data.rsi?.interpretation || getRSIInterpretation(data.rsi?.value)
                },
                macd: {
                    value: data.macd?.macd || null,
                    signal: data.macd?.signal_line || null,
                    histogram: data.macd?.histogram || null,
                    interpretation: data.macd?.signal || getMACDInterpretation(data.macd)
                },
                sma: {
                    sma20: data.sma?.sma_20 || null,
                    sma50: data.sma?.sma_50 || null,
                    signal: data.sma?.signal || 'neutral'
                },
                bollingerBands: {
                    upper: data.bollinger_bands?.upper || null,
                    middle: data.bollinger_bands?.middle || null,
                    lower: data.bollinger_bands?.lower || null,
                    signal: data.bollinger_bands?.signal || 'neutral'
                },
                volume: {
                    current: data.volume?.latest || null,
                    average: data.volume?.average || null,
                    ratio: data.volume?.ratio || 1,
                    signal: getVolumeSignal(data.volume?.ratio)
                },
                overallSignal: data.overall_signal || 'neutral'
            };

            setIndicators(normalizedIndicators);
            setLastUpdated(new Date());
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    }, [ticker]);

    useEffect(() => {
        fetchIndicators();
    }, [fetchIndicators]);

    return {
        indicators,
        loading,
        error,
        lastUpdated,
        refresh: fetchIndicators
    };
};

// Helper functions for indicator interpretation
function getSignalFromRSI(rsi) {
    if (rsi === null || rsi === undefined) return 'neutral';
    if (rsi >= 70) return 'overbought';
    if (rsi <= 30) return 'oversold';
    if (rsi >= 50) return 'bullish';
    return 'bearish';
}

function getRSIInterpretation(rsi) {
    if (rsi === null || rsi === undefined) return 'No data';
    if (rsi >= 70) return 'Overbought - Potential reversal';
    if (rsi <= 30) return 'Oversold - Potential bounce';
    if (rsi >= 50) return 'Bullish momentum';
    return 'Bearish momentum';
}

function getMACDInterpretation(macd) {
    if (!macd || macd.histogram === null) return 'neutral';
    if (macd.histogram > 0) return 'bullish';
    return 'bearish';
}

function getVolumeSignal(ratio) {
    if (!ratio) return 'neutral';
    if (ratio >= 1.5) return 'high';
    if (ratio <= 0.5) return 'low';
    return 'normal';
}

/**
 * Custom hook for fetching chart data with different timeframes.
 * 
 * @param {string} ticker - Stock ticker symbol
 * @param {string} period - Chart period (1D, 1W, 1M, 3M, 1Y)
 * @returns {object} Chart data, loading state, error
 */
export const useChartData = (ticker, period = '1M') => {
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchChartData = useCallback(async () => {
        if (!ticker) return;

        setLoading(true);
        setError(null);

        try {
            const response = await axios.get(`${API_BASE}/api/stock/${ticker}/chart?period=${period}`);

            // Format data for Recharts
            const formattedData = (response.data.data || []).map((item, index) => ({
                ...item,
                index,
                date: new Date(item.timestamp).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric'
                }),
                candleColor: item.close >= item.open ? '#10b981' : '#ef4444'
            }));

            setChartData(formattedData);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    }, [ticker, period]);

    useEffect(() => {
        fetchChartData();
    }, [fetchChartData]);

    return {
        chartData,
        loading,
        error,
        refresh: fetchChartData
    };
};

/**
 * Custom hook for fetching news with sentiment analysis.
 * 
 * @param {string} ticker - Stock ticker symbol
 * @param {number} limit - Number of articles to fetch
 * @returns {object} News articles, sentiment, loading state
 */
export const useNews = (ticker, limit = 10) => {
    const [news, setNews] = useState([]);
    const [sentiment, setSentiment] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchNews = useCallback(async () => {
        if (!ticker) return;

        setLoading(true);
        setError(null);

        try {
            const response = await axios.get(`${API_BASE}/api/stock/${ticker}/news?limit=${limit}`);

            setNews(response.data.news || []);
            setSentiment(response.data.aggregate_sentiment || null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    }, [ticker, limit]);

    useEffect(() => {
        fetchNews();
    }, [fetchNews]);

    return {
        news,
        sentiment,
        loading,
        error,
        refresh: fetchNews
    };
};

export default useTechnicals;
