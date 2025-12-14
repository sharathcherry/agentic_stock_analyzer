import { useState, useEffect, useRef, useCallback } from 'react';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/api/ws/prices';

export const useWebSocket = (onMessage, onPriceAlert) => {
    const [isConnected, setIsConnected] = useState(false);
    const [reconnectAttempts, setReconnectAttempts] = useState(0);
    const wsRef = useRef(null);
    const subscribedTickers = useRef(new Set());
    const previousPrices = useRef({});

    const connect = useCallback(() => {
        try {
            wsRef.current = new WebSocket(WS_URL);

            wsRef.current.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
                setReconnectAttempts(0);

                // Re-subscribe to all tickers
                subscribedTickers.current.forEach(ticker => {
                    wsRef.current?.send(JSON.stringify({
                        action: 'subscribe',
                        ticker: ticker
                    }));
                });
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'price_update') {
                        // Check for significant price change (>2%)
                        const ticker = data.ticker;
                        const prevPrice = previousPrices.current[ticker];

                        if (prevPrice) {
                            const changePercent = ((data.price - prevPrice) / prevPrice) * 100;

                            if (Math.abs(changePercent) >= 2 && onPriceAlert) {
                                onPriceAlert({
                                    ticker,
                                    price: data.price,
                                    changePercent,
                                    type: changePercent > 0 ? 'spike' : 'drop'
                                });
                            }
                        }

                        previousPrices.current[ticker] = data.price;
                    }

                    if (onMessage) {
                        onMessage(data);
                    }
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            wsRef.current.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);

                // Attempt to reconnect with exponential backoff
                if (reconnectAttempts < 5) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                    console.log(`Reconnecting in ${delay}ms...`);
                    setTimeout(() => {
                        setReconnectAttempts(prev => prev + 1);
                        connect();
                    }, delay);
                }
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            setIsConnected(false);
        }
    }, [onMessage, onPriceAlert, reconnectAttempts]);

    const subscribe = useCallback((ticker) => {
        subscribedTickers.current.add(ticker);

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                action: 'subscribe',
                ticker: ticker
            }));
        }
    }, []);

    const unsubscribe = useCallback((ticker) => {
        subscribedTickers.current.delete(ticker);

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                action: 'unsubscribe',
                ticker: ticker
            }));
        }
    }, []);

    const disconnect = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
    }, []);

    useEffect(() => {
        connect();

        return () => {
            disconnect();
        };
    }, []);

    return {
        isConnected,
        subscribe,
        unsubscribe,
        disconnect,
        reconnectAttempts
    };
};

export default useWebSocket;
