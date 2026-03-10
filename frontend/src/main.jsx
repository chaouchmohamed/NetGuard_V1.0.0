import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Add error boundary to catch any React errors
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('React error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '20px', 
          backgroundColor: '#0a0e1a', 
          color: '#ff2d55',
          fontFamily: 'monospace',
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>⚠️ Something went wrong</h1>
          <pre style={{ 
            backgroundColor: '#0d1117', 
            padding: '20px', 
            borderRadius: '8px',
            border: '1px solid #ff2d55',
            maxWidth: '800px',
            overflow: 'auto'
          }}>
            {this.state.error && this.state.error.toString()}
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </pre>
          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              backgroundColor: '#00f5ff',
              color: '#0a0e1a',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontFamily: 'monospace',
              fontWeight: 'bold'
            }}
          >
            Reload Application
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Add console log to verify React is loading
console.log('🚀 NetGuard React app starting...');

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)