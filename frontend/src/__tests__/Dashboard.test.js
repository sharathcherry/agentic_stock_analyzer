import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import StockDashboard from '../components/Dashboard/StockDashboard';
import PriceChart from '../components/Dashboard/PriceChart';
import PredictionHistory from '../components/Dashboard/PredictionHistory';
import ToastNotifications, { useToast } from '../components/Dashboard/ToastNotifications';
import ErrorBoundary, { LoadingSkeleton, EmptyState } from '../components/ErrorBoundary';

// Mock axios
jest.mock('axios', () => ({
    get: jest.fn(),
    post: jest.fn()
}));

const axios = require('axios');

describe('StockDashboard Component', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        localStorage.clear();
    });

    test('renders dashboard header', () => {
        render(<StockDashboard />);
        expect(screen.getByText(/Stock Analysis Dashboard/i)).toBeInTheDocument();
    });

    test('renders stock selector', () => {
        render(<StockDashboard />);
        expect(screen.getByText(/Select Stock/i)).toBeInTheDocument();
    });

    test('shows analyze button', () => {
        render(<StockDashboard />);
        expect(screen.getByRole('button', { name: /Analyze/i })).toBeInTheDocument();
    });

    test('filters stocks on search', () => {
        render(<StockDashboard />);
        const searchInput = screen.getByPlaceholderText(/Search stocks/i);
        fireEvent.change(searchInput, { target: { value: 'RELIANCE' } });
        // Dropdown should show filtered results
        expect(searchInput.value).toBe('RELIANCE');
    });

    test('saves selected stock to localStorage', () => {
        render(<StockDashboard />);
        // Default stock should be saved
        expect(localStorage.getItem('lastSelectedStock')).toBeTruthy();
    });
});

describe('PriceChart Component', () => {
    test('renders loading state', () => {
        render(<PriceChart symbol="RELIANCE.NS" />);
        // Initially shows loading or chart
        expect(screen.getByText(/Price Chart/i)).toBeInTheDocument();
    });

    test('renders timeframe buttons', () => {
        render(<PriceChart symbol="RELIANCE.NS" />);
        expect(screen.getByText('1D')).toBeInTheDocument();
        expect(screen.getByText('1W')).toBeInTheDocument();
        expect(screen.getByText('1M')).toBeInTheDocument();
        expect(screen.getByText('3M')).toBeInTheDocument();
        expect(screen.getByText('1Y')).toBeInTheDocument();
    });

    test('renders indicator checkboxes', () => {
        render(<PriceChart symbol="RELIANCE.NS" />);
        expect(screen.getByLabelText(/SMA 20/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/SMA 50/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Bollinger Bands/i)).toBeInTheDocument();
    });

    test('toggles indicator visibility', () => {
        render(<PriceChart symbol="RELIANCE.NS" />);
        const sma20Checkbox = screen.getByLabelText(/SMA 20/i);
        expect(sma20Checkbox).toBeChecked();

        fireEvent.click(sma20Checkbox);
        expect(sma20Checkbox).not.toBeChecked();
    });
});

describe('PredictionHistory Component', () => {
    test('renders prediction history header', () => {
        render(<PredictionHistory symbol="RELIANCE.NS" />);
        expect(screen.getByText(/Prediction History/i)).toBeInTheDocument();
    });

    test('renders export CSV button', () => {
        render(<PredictionHistory symbol="RELIANCE.NS" />);
        expect(screen.getByText(/Export CSV/i)).toBeInTheDocument();
    });

    test('renders accuracy badge', async () => {
        render(<PredictionHistory symbol="RELIANCE.NS" />);
        await waitFor(() => {
            expect(screen.getByText(/Accuracy:/i)).toBeInTheDocument();
        });
    });
});

describe('ErrorBoundary Component', () => {
    const ThrowError = () => {
        throw new Error('Test error');
    };

    test('catches errors and displays fallback', () => {
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => { });

        render(
            <ErrorBoundary>
                <ThrowError />
            </ErrorBoundary>
        );

        expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
        consoleSpy.mockRestore();
    });

    test('renders children when no error', () => {
        render(
            <ErrorBoundary>
                <div>Child content</div>
            </ErrorBoundary>
        );

        expect(screen.getByText('Child content')).toBeInTheDocument();
    });
});

describe('LoadingSkeleton Component', () => {
    test('renders card skeleton', () => {
        const { container } = render(<LoadingSkeleton type="card" />);
        expect(container.querySelector('.skeleton-card')).toBeInTheDocument();
    });

    test('renders multiple skeletons', () => {
        const { container } = render(<LoadingSkeleton type="card" count={3} />);
        expect(container.querySelectorAll('.skeleton-card').length).toBe(3);
    });

    test('renders chart skeleton', () => {
        const { container } = render(<LoadingSkeleton type="chart" />);
        expect(container.querySelector('.skeleton-chart')).toBeInTheDocument();
    });

    test('renders indicator skeleton', () => {
        const { container } = render(<LoadingSkeleton type="indicator" />);
        expect(container.querySelector('.skeleton-indicator')).toBeInTheDocument();
    });
});

describe('EmptyState Component', () => {
    test('renders with default props', () => {
        render(<EmptyState />);
        expect(screen.getByText(/No Data Available/i)).toBeInTheDocument();
    });

    test('renders with custom message', () => {
        render(<EmptyState title="Custom Title" message="Custom message" />);
        expect(screen.getByText('Custom Title')).toBeInTheDocument();
        expect(screen.getByText('Custom message')).toBeInTheDocument();
    });

    test('renders action button when provided', () => {
        const handleAction = jest.fn();
        render(<EmptyState action={handleAction} actionLabel="Click me" />);

        const button = screen.getByText('Click me');
        fireEvent.click(button);
        expect(handleAction).toHaveBeenCalled();
    });
});

describe('ToastNotifications Component', () => {
    test('renders without toasts', () => {
        const { container } = render(
            <ToastNotifications
                toasts={[]}
                removeToast={() => { }}
                soundEnabled={false}
                toggleSound={() => { }}
            />
        );
        expect(container.querySelector('.toast-container')).toBeInTheDocument();
    });

    test('renders toasts', () => {
        const toasts = [
            { id: 1, message: 'Test message', type: 'success' }
        ];

        render(
            <ToastNotifications
                toasts={toasts}
                removeToast={() => { }}
                soundEnabled={false}
                toggleSound={() => { }}
            />
        );

        expect(screen.getByText('Test message')).toBeInTheDocument();
    });

    test('removes toast on click', () => {
        const removeToast = jest.fn();
        const toasts = [
            { id: 1, message: 'Removable toast', type: 'info' }
        ];

        render(
            <ToastNotifications
                toasts={toasts}
                removeToast={removeToast}
                soundEnabled={false}
                toggleSound={() => { }}
            />
        );

        fireEvent.click(screen.getByText('Removable toast'));
        expect(removeToast).toHaveBeenCalledWith(1);
    });

    test('toggles sound on button click', () => {
        const toggleSound = jest.fn();

        render(
            <ToastNotifications
                toasts={[]}
                removeToast={() => { }}
                soundEnabled={false}
                toggleSound={toggleSound}
            />
        );

        fireEvent.click(screen.getByTitle(/Enable sound alerts/i));
        expect(toggleSound).toHaveBeenCalled();
    });
});

describe('Custom Hooks Integration', () => {
    test('useStock hook exports exist', () => {
        const { useStock, useAnalysis, usePredictions } = require('../hooks/useStock');
        expect(typeof useStock).toBe('function');
        expect(typeof useAnalysis).toBe('function');
        expect(typeof usePredictions).toBe('function');
    });

    test('useTechnicals hook exports exist', () => {
        const { useTechnicals, useChartData, useNews } = require('../hooks/useTechnicals');
        expect(typeof useTechnicals).toBe('function');
        expect(typeof useChartData).toBe('function');
        expect(typeof useNews).toBe('function');
    });

    test('useWebSocket hook exports exist', () => {
        const { useWebSocket } = require('../hooks/useWebSocket');
        expect(typeof useWebSocket).toBe('function');
    });
});

describe('Types Definition', () => {
    test('types module loads without errors', () => {
        expect(() => require('../types/index')).not.toThrow();
    });
});
