import React from 'react';
import './ErrorBoundary.css';

/**
 * Error Boundary component for catching and handling React errors.
 * Provides fallback UI and error reporting.
 */
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null
        };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({ errorInfo });

        // Log error to console (could send to error reporting service)
        console.error('Error Boundary caught an error:', error, errorInfo);
    }

    handleRetry = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    handleReload = () => {
        window.location.reload();
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary">
                    <div className="error-content">
                        <div className="error-icon">⚠️</div>
                        <h2>Something went wrong</h2>
                        <p className="error-message">
                            {this.state.error?.message || 'An unexpected error occurred'}
                        </p>

                        {this.props.showDetails && this.state.errorInfo && (
                            <details className="error-details">
                                <summary>Error Details</summary>
                                <pre>{this.state.errorInfo.componentStack}</pre>
                            </details>
                        )}

                        <div className="error-actions">
                            <button className="retry-btn" onClick={this.handleRetry}>
                                Try Again
                            </button>
                            <button className="reload-btn" onClick={this.handleReload}>
                                Reload Page
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

/**
 * Functional error fallback component for use with error boundaries.
 */
export const ErrorFallback = ({ error, resetErrorBoundary }) => (
    <div className="error-fallback">
        <div className="error-icon">❌</div>
        <h3>Error Loading Component</h3>
        <p>{error?.message || 'Something went wrong'}</p>
        <button onClick={resetErrorBoundary}>Retry</button>
    </div>
);

/**
 * Loading skeleton component for optimistic UI updates.
 */
export const LoadingSkeleton = ({ type = 'card', count = 1 }) => {
    const skeletons = Array(count).fill(null);

    const renderSkeleton = (key) => {
        switch (type) {
            case 'card':
                return (
                    <div key={key} className="skeleton-card">
                        <div className="skeleton-line skeleton-title"></div>
                        <div className="skeleton-line skeleton-text"></div>
                        <div className="skeleton-line skeleton-text short"></div>
                    </div>
                );
            case 'chart':
                return (
                    <div key={key} className="skeleton-chart">
                        <div className="skeleton-chart-area"></div>
                    </div>
                );
            case 'indicator':
                return (
                    <div key={key} className="skeleton-indicator">
                        <div className="skeleton-circle"></div>
                        <div className="skeleton-line skeleton-text"></div>
                    </div>
                );
            case 'price':
                return (
                    <div key={key} className="skeleton-price">
                        <div className="skeleton-line skeleton-big"></div>
                        <div className="skeleton-line skeleton-text short"></div>
                    </div>
                );
            default:
                return (
                    <div key={key} className="skeleton-line"></div>
                );
        }
    };

    return (
        <div className="loading-skeleton">
            {skeletons.map((_, index) => renderSkeleton(index))}
        </div>
    );
};

/**
 * Empty state component for when data is not available.
 */
export const EmptyState = ({
    icon = '📊',
    title = 'No Data Available',
    message = 'Try refreshing or selecting a different stock.',
    action,
    actionLabel = 'Refresh'
}) => (
    <div className="empty-state">
        <div className="empty-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{message}</p>
        {action && (
            <button className="empty-action" onClick={action}>
                {actionLabel}
            </button>
        )}
    </div>
);

export default ErrorBoundary;
