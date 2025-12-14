import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Custom hook for fetching and managing stock data.
 * Handles real-time price updates, OHLC data, and caching.
 * 
 * @param {string} ticker - Stock ticker symbol (e.g., 'RELIANCE.NS')
 * @param {number} refreshInterval - Price refresh interval in ms (default: 5000)
 * @returns {object} Stock data, loading state, error, and refresh function
 */
export const useStock = (ticker, refreshInterval = 5000) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);

    const fetchStockData = useCallback(async () => {
        if (!ticker) return;

        try {
            const response = await axios.get(`${API_BASE}/api/stock/${ticker}/realtime`);

            setData(prev => {
                // Optimistic update - detect price change direction
                const newData = {
                    ...response.data,
                    priceDirection: prev?.price
                        ? response.data.price > prev.price ? 'up' : response.data.price < prev.price ? 'down' : null
                        : null,
                    previousPrice: prev?.price
                };
                return newData;
            });

            setLastUpdated(new Date());
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
    }, [ticker]);

    const fetchFullData = useCallback(async () => {
        if (!ticker) return;

        setLoading(true);
        setError(null);

        try {
            const response = await axios.get(`${API_BASE}/api/stock/${ticker}/realtime`);
            setData(response.data);
            setLastUpdated(new Date());
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    }, [ticker]);

    // Initial fetch
    useEffect(() => {
        fetchFullData();
    }, [fetchFullData]);

    // Auto-refresh
    useEffect(() => {
        if (!ticker || refreshInterval <= 0) return;

        const interval = setInterval(fetchStockData, refreshInterval);
        return () => clearInterval(interval);
    }, [ticker, refreshInterval, fetchStockData]);

    const refresh = useCallback(() => {
        fetchFullData();
    }, [fetchFullData]);

    return {
        data,
        loading,
        error,
        lastUpdated,
        refresh,
        priceDirection: data?.priceDirection
    };
};

/**
 * Custom hook for fetching stock analysis results.
 * Triggers AI multi-model analysis and manages results.
 * 
 * @param {string} ticker - Stock ticker symbol
 * @returns {object} Analysis data, loading state, error, and analyze function
 */
export const useAnalysis = (ticker) => {
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [analysisTime, setAnalysisTime] = useState(null);

    const analyze = useCallback(async () => {
        if (!ticker) return;

        setLoading(true);
        setError(null);
        const startTime = Date.now();

        try {
            const cleanSymbol = ticker.replace('.NS', '').replace('.BO', '');

            const response = await axios.post(`${API_BASE}/api/get_stock_analysis_multimodel`, {
                symbol: cleanSymbol,
                exchange: 'NSE'
            });

            setAnalysis(response.data);
            setAnalysisTime((Date.now() - startTime) / 1000);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    }, [ticker]);

    // Reset analysis when ticker changes
    useEffect(() => {
        setAnalysis(null);
        setError(null);
    }, [ticker]);

    return {
        analysis,
        loading,
        error,
        analysisTime,
        analyze
    };
};

/**
 * Custom hook for managing prediction history.
 * Fetches and paginates prediction records.
 * 
 * @param {string} ticker - Stock ticker symbol
 * @param {number} limit - Number of predictions to fetch
 * @returns {object} Predictions data, pagination, and loading state
 */
export const usePredictions = (ticker, limit = 50) => {
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [accuracy, setAccuracy] = useState(0);

    const fetchPredictions = useCallback(async () => {
        if (!ticker) return;

        setLoading(true);
        setError(null);

        try {
            const cleanSymbol = ticker.replace('.NS', '').replace('.BO', '');
            const response = await axios.get(`${API_BASE}/api/predictions/${cleanSymbol}?limit=${limit}`);

            const data = response.data.predictions || [];
            setPredictions(data);

            // Calculate accuracy
            const validated = data.filter(p => p.status === 'CORRECT' || p.status === 'INCORRECT');
            if (validated.length > 0) {
                const correct = validated.filter(p => p.status === 'CORRECT').length;
                setAccuracy((correct / validated.length) * 100);
            }
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    }, [ticker, limit]);

    useEffect(() => {
        fetchPredictions();
    }, [fetchPredictions]);

    return {
        predictions,
        loading,
        error,
        accuracy,
        refresh: fetchPredictions
    };
};

export default useStock;
