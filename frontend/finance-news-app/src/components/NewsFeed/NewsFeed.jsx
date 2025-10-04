import React, { useState } from 'react';
import { AiFillFire } from 'react-icons/ai';
import { BiSolidUpArrow } from 'react-icons/bi';
import { mockNews } from '../../data/mockData';
import { useNewsStore } from '../../store/newsStore';
import './NewsFeed.css';

const NewsFeed = () => {
  const [sortBy, setSortBy] = useState('hottest');
  const [sentimentFilter, setSentimentFilter] = useState('all');
  const [sourceFilter, setSourceFilter] = useState('all');
  const setSelectedNews = useNewsStore((state) => state.setSelectedNews);

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return '#4CAF50';
      case 'negative':
        return '#F44336';
      default:
        return '#FF9800';
    }
  };

  const getSentimentLabel = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'Позитив';
      case 'negative':
        return 'Негатив';
      default:
        return 'Нейтрал';
    }
  };

  return (
    <div className="news-feed">
      {/* Header */}
      <div className="news-feed-header">
        <h1 className="news-feed-title">Лента новостей</h1>
        <span className="news-date">4.10.2025</span>
      </div>

      {/* Filters */}
      <div className="news-filters">
        <div className="filter-dropdown">
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select"
          >
            <option value="hottest">Самые горячие</option>
            <option value="recent">Самые новые</option>
            <option value="popular">Популярные</option>
          </select>
        </div>

        <div className="filter-dropdown">
          <select 
            value={sentimentFilter} 
            onChange={(e) => setSentimentFilter(e.target.value)}
            className="filter-select"
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
          >
            <option value="all">Источник</option>
            <option value="source1">Источник 1</option>
            <option value="source2">Источник 2</option>
          </select>
        </div>
      </div>

      {/* News List */}
      <div className="news-list">
        {mockNews.map((news) => (
          <div 
            key={news.id} 
            className="news-card"
            onClick={() => setSelectedNews(news)}
          >
            <div className="news-card-header">
              <h3 className="news-title">
                {news.title.split('#')[0]}
                <span className="news-ticker">#{news.company}</span>
                {news.title.split('#')[1]?.replace(news.company, '')}
              </h3>
              <div className="news-hotness">
                {/*<span className="hotness-value">{news.hotness}</span>*/}
                <AiFillFire color="#FF6B35" size={30} />
              </div>
            </div>

            <p className="news-description">{news.description}</p>

            <button className="read-more-btn">
              Подробнее →
            </button>

            <div className="news-footer">
              <span className="news-source">{news.source}</span>
              <span 
                className="news-sentiment"
                style={{ color: getSentimentColor(news.sentiment) }}
              >
                {getSentimentLabel(news.sentiment)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NewsFeed;