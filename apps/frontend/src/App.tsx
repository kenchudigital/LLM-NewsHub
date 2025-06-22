import React from 'react';
import { Routes, Route } from 'react-router-dom';
import NewsPortal from './components/NewsPortal';
import ArticlePage from './components/ArticlePage';

function App() {
    return (
        <Routes>
            <Route path="/" element={<NewsPortal />} />
            <Route path="/article/:date/:groupId" element={<ArticlePage />} />
        </Routes>
    );
}

export default App; 