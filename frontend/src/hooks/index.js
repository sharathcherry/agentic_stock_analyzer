/**
 * Custom Hooks Index
 * Export all custom hooks for easy importing.
 */

// Stock data hooks
export { useStock, useAnalysis, usePredictions } from './useStock';

// Technical indicators hooks
export { useTechnicals, useChartData, useNews } from './useTechnicals';

// WebSocket hook
export { useWebSocket } from './useWebSocket';

// Re-export default
export { default as useStockDefault } from './useStock';
export { default as useTechnicalsDefault } from './useTechnicals';
export { default as useWebSocketDefault } from './useWebSocket';
