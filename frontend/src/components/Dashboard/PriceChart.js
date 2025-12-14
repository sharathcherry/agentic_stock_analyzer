import React, { useState, useEffect } from 'react';
import {
    ComposedChart,
    Line,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ReferenceLine,
    Area
} from 'recharts';
import './PriceChart.css';

const TIMEFRAMES = [
    { label: '1D', value: '1d', days: 1 },
    { label: '1W', value: '1w', days: 7 },
    { label: '1M', value: '1m', days: 30 },
    { label: '3M', value: '3m', days: 90 },
    { label: '1Y', value: '1y', days: 365 }
];

const PriceChart = ({ symbol, technicalIndicators, prediction }) => {
    const [timeframe, setTimeframe] = useState('1m');
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showSMA20, setShowSMA20] = useState(true);
    const [showSMA50, setShowSMA50] = useState(true);
    const [showBB, setShowBB] = useState(false);

    useEffect(() => {
        if (symbol) {
            fetchChartData();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [symbol, timeframe]);

    const fetchChartData = async () => {
        setLoading(true);
        try {
            // Mock data for demonstration - replace with actual API call
            const days = TIMEFRAMES.find(tf => tf.value === timeframe)?.days || 30;
            const mockData = generateMockData(days);
            setChartData(mockData);
        } catch (error) {
            console.error('Error fetching chart data:', error);
        } finally {
            setLoading(false);
        }
    };

    const generateMockData = (days) => {
        const data = [];
        let basePrice = 2450;
        const today = new Date();

        for (let i = days; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);

            const open = basePrice + (Math.random() - 0.5) * 40;
            const close = open + (Math.random() - 0.5) * 60;
            const high = Math.max(open, close) + Math.random() * 30;
            const low = Math.min(open, close) - Math.random() * 30;
            const volume = Math.random() * 10000000 + 5000000;

            // Calculate SMAs
            const sma20 = basePrice + (Math.random() - 0.5) * 20;
            const sma50 = basePrice + (Math.random() - 0.5) * 30;

            // Bollinger Bands
            const bb_middle = sma20;
            const bb_upper = bb_middle + 50;
            const bb_lower = bb_middle - 50;

            data.push({
                date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                timestamp: date.getTime(),
                open: parseFloat(open.toFixed(2)),
                high: parseFloat(high.toFixed(2)),
                low: parseFloat(low.toFixed(2)),
                close: parseFloat(close.toFixed(2)),
                volume: Math.floor(volume),
                sma20: parseFloat(sma20.toFixed(2)),
                sma50: parseFloat(sma50.toFixed(2)),
                bb_upper: parseFloat(bb_upper.toFixed(2)),
                bb_middle: parseFloat(bb_middle.toFixed(2)),
                bb_lower: parseFloat(bb_lower.toFixed(2)),
                candleColor: close >= open ? '#10b981' : '#ef4444'
            });

            basePrice = close;
        }

        return data;
    };

    // CustomCandlestick component for future candlestick chart implementation
    // Currently using line chart for price visualization

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="chart-tooltip">
                    <p className="tooltip-date">{data.date}</p>
                    <div className="tooltip-prices">
                        <p>Open: <span>₹{data.open}</span></p>
                        <p>High: <span className="high">₹{data.high}</span></p>
                        <p>Low: <span className="low">₹{data.low}</span></p>
                        <p>Close: <span>₹{data.close}</span></p>
                    </div>
                    <p className="tooltip-volume">Volume: {(data.volume / 1000000).toFixed(2)}M</p>
                    {showSMA20 && <p>SMA 20: <span>₹{data.sma20}</span></p>}
                    {showSMA50 && <p>SMA 50: <span>₹{data.sma50}</span></p>}
                </div>
            );
        }
        return null;
    };

    const targetPrice = prediction?.target_price;
    const stopLoss = prediction?.stop_loss;

    return (
        <div className="price-chart-container">
            <div className="chart-header">
                <h3>📈 Price Chart</h3>
                <div className="chart-controls">
                    <div className="timeframe-selector">
                        {TIMEFRAMES.map(tf => (
                            <button
                                key={tf.value}
                                className={`timeframe-btn ${timeframe === tf.value ? 'active' : ''}`}
                                onClick={() => setTimeframe(tf.value)}
                            >
                                {tf.label}
                            </button>
                        ))}
                    </div>
                    <div className="indicator-toggles">
                        <label>
                            <input
                                type="checkbox"
                                checked={showSMA20}
                                onChange={(e) => setShowSMA20(e.target.checked)}
                            />
                            SMA 20
                        </label>
                        <label>
                            <input
                                type="checkbox"
                                checked={showSMA50}
                                onChange={(e) => setShowSMA50(e.target.checked)}
                            />
                            SMA 50
                        </label>
                        <label>
                            <input
                                type="checkbox"
                                checked={showBB}
                                onChange={(e) => setShowBB(e.target.checked)}
                            />
                            Bollinger Bands
                        </label>
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="chart-loading">
                    <div className="spinner"></div>
                    <p>Loading chart data...</p>
                </div>
            ) : (
                <>
                    <ResponsiveContainer width="100%" height={400}>
                        <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis
                                dataKey="date"
                                stroke="#94a3b8"
                                style={{ fontSize: '12px' }}
                            />
                            <YAxis
                                stroke="#94a3b8"
                                domain={['auto', 'auto']}
                                style={{ fontSize: '12px' }}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend />

                            {/* Bollinger Bands */}
                            {showBB && (
                                <>
                                    <Area
                                        type="monotone"
                                        dataKey="bb_upper"
                                        stroke="#667eea"
                                        fill="#667eea"
                                        fillOpacity={0.1}
                                        strokeWidth={1}
                                        dot={false}
                                        name="BB Upper"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="bb_lower"
                                        stroke="#667eea"
                                        fill="#667eea"
                                        fillOpacity={0.1}
                                        strokeWidth={1}
                                        dot={false}
                                        name="BB Lower"
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="bb_middle"
                                        stroke="#667eea"
                                        strokeWidth={1}
                                        dot={false}
                                        name="BB Middle"
                                    />
                                </>
                            )}

                            {/* SMA Lines */}
                            {showSMA20 && (
                                <Line
                                    type="monotone"
                                    dataKey="sma20"
                                    stroke="#f59e0b"
                                    strokeWidth={2}
                                    dot={false}
                                    name="SMA 20"
                                />
                            )}
                            {showSMA50 && (
                                <Line
                                    type="monotone"
                                    dataKey="sma50"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    dot={false}
                                    name="SMA 50"
                                />
                            )}

                            {/* Price Line (for simple line chart appearance) */}
                            <Line
                                type="monotone"
                                dataKey="close"
                                stroke="#10b981"
                                strokeWidth={2}
                                dot={false}
                                name="Close Price"
                            />

                            {/* Target Price Line */}
                            {targetPrice && (
                                <ReferenceLine
                                    y={targetPrice}
                                    stroke="#10b981"
                                    strokeDasharray="5 5"
                                    strokeWidth={2}
                                    label={{
                                        value: `Target: ₹${targetPrice.toFixed(2)}`,
                                        fill: '#10b981',
                                        fontSize: 12,
                                        position: 'right'
                                    }}
                                />
                            )}

                            {/* Stop Loss Line */}
                            {stopLoss && (
                                <ReferenceLine
                                    y={stopLoss}
                                    stroke="#ef4444"
                                    strokeDasharray="5 5"
                                    strokeWidth={2}
                                    label={{
                                        value: `Stop Loss: ₹${stopLoss.toFixed(2)}`,
                                        fill: '#ef4444',
                                        fontSize: 12,
                                        position: 'right'
                                    }}
                                />
                            )}
                        </ComposedChart>
                    </ResponsiveContainer>

                    {/* Volume Chart */}
                    <ResponsiveContainer width="100%" height={100}>
                        <ComposedChart data={chartData} margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
                            <XAxis
                                dataKey="date"
                                stroke="#94a3b8"
                                style={{ fontSize: '10px' }}
                                hide
                            />
                            <YAxis
                                stroke="#94a3b8"
                                style={{ fontSize: '10px' }}
                            />
                            <Tooltip
                                content={({ active, payload }) => {
                                    if (active && payload && payload.length) {
                                        return (
                                            <div className="chart-tooltip">
                                                <p>Volume: {(payload[0].value / 1000000).toFixed(2)}M</p>
                                            </div>
                                        );
                                    }
                                    return null;
                                }}
                            />
                            <Bar
                                dataKey="volume"
                                fill="#667eea"
                                opacity={0.6}
                                name="Volume"
                            />
                        </ComposedChart>
                    </ResponsiveContainer>

                    {/* Chart Legend */}
                    <div className="chart-legend">
                        <span className="legend-item">
                            <span className="legend-color" style={{ background: '#10b981' }}></span>
                            Close Price
                        </span>
                        {showSMA20 && (
                            <span className="legend-item">
                                <span className="legend-color" style={{ background: '#f59e0b' }}></span>
                                SMA 20
                            </span>
                        )}
                        {showSMA50 && (
                            <span className="legend-item">
                                <span className="legend-color" style={{ background: '#3b82f6' }}></span>
                                SMA 50
                            </span>
                        )}
                        {showBB && (
                            <span className="legend-item">
                                <span className="legend-color" style={{ background: '#667eea' }}></span>
                                Bollinger Bands
                            </span>
                        )}
                    </div>
                </>
            )}
        </div>
    );
};

export default PriceChart;
