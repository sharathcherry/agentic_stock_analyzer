import React, { useState, useEffect, useCallback } from 'react';
import './ToastNotifications.css';

// Sound effect URLs (using web audio)
const SOUND_URLS = {
    priceSpike: 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA',
    priceDrop: 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA',
    alert: 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA'
};

export const useToast = () => {
    const [toasts, setToasts] = useState([]);
    const [soundEnabled, setSoundEnabled] = useState(() => {
        return localStorage.getItem('soundEnabled') === 'true';
    });

    const playSound = useCallback((type) => {
        if (!soundEnabled) return;

        try {
            const audio = new Audio(SOUND_URLS[type] || SOUND_URLS.alert);
            audio.volume = 0.5;
            audio.play().catch(() => { }); // Ignore autoplay restrictions
        } catch (e) {
            console.log('Sound not supported');
        }
    }, [soundEnabled]);

    const addToast = useCallback((message, type = 'info', duration = 5000) => {
        const id = Date.now();
        const toast = { id, message, type };

        setToasts(prev => [...prev, toast]);

        // Play sound for important notifications
        if (type === 'success' || type === 'warning' || type === 'error') {
            playSound(type === 'error' ? 'priceDrop' : 'priceSpike');
        }

        // Auto-remove after duration
        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id));
        }, duration);

        return id;
    }, [playSound]);

    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    }, []);

    const toggleSound = useCallback(() => {
        setSoundEnabled(prev => {
            const newValue = !prev;
            localStorage.setItem('soundEnabled', String(newValue));
            return newValue;
        });
    }, []);

    return { toasts, addToast, removeToast, soundEnabled, toggleSound };
};

const ToastNotifications = ({ toasts, removeToast, soundEnabled, toggleSound }) => {
    const getIcon = (type) => {
        switch (type) {
            case 'success': return '✅';
            case 'warning': return '⚠️';
            case 'error': return '🔴';
            case 'price-up': return '📈';
            case 'price-down': return '📉';
            case 'prediction': return '🤖';
            case 'market': return '🏪';
            default: return 'ℹ️';
        }
    };

    return (
        <div className="toast-container">
            {/* Sound Toggle */}
            <button
                className={`sound-toggle ${soundEnabled ? 'enabled' : ''}`}
                onClick={toggleSound}
                title={soundEnabled ? 'Disable sound alerts' : 'Enable sound alerts'}
            >
                {soundEnabled ? '🔔' : '🔕'}
            </button>

            {/* Toast Messages */}
            {toasts.map(toast => (
                <div
                    key={toast.id}
                    className={`toast toast-${toast.type}`}
                    onClick={() => removeToast(toast.id)}
                >
                    <span className="toast-icon">{getIcon(toast.type)}</span>
                    <span className="toast-message">{toast.message}</span>
                    <button className="toast-close" onClick={(e) => {
                        e.stopPropagation();
                        removeToast(toast.id);
                    }}>×</button>
                </div>
            ))}
        </div>
    );
};

export default ToastNotifications;
