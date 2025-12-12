import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';


const root = ReactDOM.createRoot(document.getElementById('root'));
// StrictMode rimosso per ottimizzare prestazioni in produzione
// (causa doppi render in development)
root.render(<App />);

