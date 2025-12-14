import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import StockDashboard from './components/Dashboard/StockDashboard';
import ErrorBoundary from './components/ErrorBoundary';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <ErrorBoundary showDetails={process.env.NODE_ENV === 'development'}>
            <StockDashboard />
        </ErrorBoundary>
    </React.StrictMode>
);
