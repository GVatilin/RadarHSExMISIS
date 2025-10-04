import React, { useState, useEffect } from 'react';
import { AiFillFire } from 'react-icons/ai';
import { useNewsStore } from '../../store/newsStore';
import { getSentimentColor, getSentimentText, isHotNews, formatDate } from '../../utils/helpers';
import './NewsFeed.css';

const NewsFeed = () => {
  const [sortBy, setSortBy] = useState('hottest');
  const [sentimentFilter, setSentimentFilter] = useState('all');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [hoursInput, setHoursInput] = useState(24);
  
  const { 
    news, 
    loading, 
    error, 
    viewMode,
    hotNewsHours,
    fetchAllNews, 
    fetchHotNews,
    setSelectedNews,
    setFilter,
    getFilteredNews
  } = useNewsStore();

  // Загрузка всех новостей при монтировании
  useEffect(() => {
    fetchAllNews();
  }, [fetchAllNews]);

  // Применение фильтров
  useEffect(() => {
    setFilter('sortBy', sortBy);
    setFilter('sentiment', sentimentFilter);
    setFilter('source', sourceFilter);
  }, [sortBy, sentimentFilter, sourceFilter, setFilter]);

  const filteredNews = getFilteredNews();

  // Получить уникальные источники
  const uniqueSources = [...new Set(news.flatMap(n => n.sources || []))];

  const handleGetHotNews = () => {
    fetchHotNews(hoursInput);
  };

  const handleGetAllNews = () => {
    fetchAllNews();
  };

  return (
    <div className="news-feed">
      {/* Header */}
      <div className="news-feed-header">
        <h1 className="news-feed-title">Лента новостей</h1>
        <span className="news-date">
          {new Date().toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'numeric',
            year: 'numeric'
          })}
        </span>
      </div>

      {/* Hot News Controls */}
      <div className="hot-news-controls">
        <button 
          className={`view-mode-btn ${viewMode === 'all' ? 'active' : ''}`}
          onClick={handleGetAllNews}
          disabled={loading}
        >
          Все новости
        </button>
        
        <div className="hot-news-input-group">
          <input
            type="number"
            min="1"
            max="168"
            value={hoursInput}
            onChange={(e) => setHoursInput(Number(e.target.value))}
            className="hours-input"
            placeholder="Часы"
          />
          <button 
            className={`view-mode-btn ${viewMode === 'hot' ? 'active' : ''}`}
            onClick={handleGetHotNews}
            disabled={loading}
          >
            🔥 Топ-5 горячих за {hoursInput}ч
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="news-filters">
        <div className="filter-dropdown">
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="hottest">Самые горячие</option>
            <option value="recent">Самые новые</option>
          </select>
        </div>

        <div className="filter-dropdown">
          <select 
            value={sentimentFilter} 
            onChange={(e) => setSentimentFilter(e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="all">Тональность</option>
            <option value="positive">Позитив</option>
            <option value="neutral">Нейтрал</option>
            <option value="negative">Негатив</option>
          </select>
        </div>

        <div className="filter-dropdown">
          <select 
            value={sourceFilter} 
            onChange={(e) => setSourceFilter(e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="all">Источник</option>
            {uniqueSources.map((source, index) => (
              <option key={index} value={source}>{source}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Загрузка новостей...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="error-state">
          <p>Ошибка загрузки: {error}</p>
          <button onClick={fetchAllNews} className="retry-btn">
            Попробовать снова
          </button>
        </div>
      )}

      {/* News List */}
      {!loading && !error && (
        <div className="news-list">
          {filteredNews.length === 0 ? (
            <div className="empty-state">
              <p>Новостей не найдено</p>
            </div>
          ) : (
            filteredNews.map((newsItem, index) => (
              <div 
                key={index} 
                className={`news-card ${isHotNews(newsItem.hotness) ? 'hot-news' : ''}`}
                onClick={() => setSelectedNews(newsItem)}
              >
                <div className="news-card-header">
                  <h3 className="news-title">
                    {newsItem.headline}
                    {newsItem.entities && newsItem.entities.length > 0 && (
                      <span className="news-ticker"> #{newsItem.entities[0]}</span>
                    )}
                    {isHotNews(newsItem.hotness) && (
                      <span className="hot-badge">🔥 Горячая</span>
                    )}
                  </h3>
                  <div className="news-hotness">
                    <span className="hotness-value">{newsItem.hotness || 0}</span>
                    <AiFillFire color="#FF6B35" size={20} />
                  </div>
                </div>

                <p className="news-description">{newsItem.text}</p>

                {newsItem.why_now && (
                  <div className="why-now">
                    <strong>Почему сейчас:</strong> {newsItem.why_now}
                  </div>
                )}

                <button className="read-more-btn">
                  Подробнее →
                </button>

                <div className="news-footer">
                  <div className="news-footer-left">
                    {newsItem.sources && newsItem.sources.length > 0 && (
                      <span className="news-source">{newsItem.sources[0]}</span>
                    )}
                    {newsItem.timeline && newsItem.timeline.length > 0 && (
                      <span className="news-date-footer">
                        {formatDate(newsItem.timeline[0].date)}
                      </span>
                    )}
                  </div>
                  <span 
                    className="news-sentiment"
                    style={{ color: getSentimentColor(newsItem.sentiment) }}
                  >
                    {getSentimentText(newsItem.sentiment)}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default NewsFeed;