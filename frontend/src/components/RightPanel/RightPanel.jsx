import React, { useState } from 'react';
import { BiPencil } from 'react-icons/bi';
import { AiOutlineSmile, AiOutlineLike, AiFillFire } from 'react-icons/ai';
import { BsGraphUp } from 'react-icons/bs';
import { useNewsStore } from '../../store/newsStore';
import { getSentimentColor, getSentimentText, formatDate } from '../../utils/helpers';
import './RightPanel.css';

const RightPanel = () => {
  const [draftText, setDraftText] = useState('');
  const selectedNews = useNewsStore((state) => state.selectedNews);

  const handleSubmitDraft = () => {
    if (!draftText.trim()) {
      alert('Напишите текст черновика');
      return;
    }
    
    console.log('Draft submitted:', {
      text: draftText,
      news: selectedNews
    });
    
    // Здесь будет отправка на бэкенд
    alert('Черновик создан!');
    setDraftText('');
  };

  const handleCopyNews = () => {
    if (selectedNews) {
      const textToCopy = `${selectedNews.headline}\n\n${selectedNews.text}\n\n${selectedNews.why_now || ''}`;
      navigator.clipboard.writeText(textToCopy);
      alert('Новость скопирована в буфер обмена');
    }
  };

  return (
    <div className="right-panel">
      {/* Header */}
      <div className="assistant-header">
        <BiPencil size={24} color="#9C27B0" />
        <h2 className="assistant-title">Ассистент</h2>
      </div>

      {/* Selected News Preview */}
      {selectedNews ? (
        <div className="selected-news-preview">
          <h3 className="preview-title">
            {selectedNews.headline}
            {selectedNews.entities && selectedNews.entities.length > 0 && (
              <span className="preview-ticker"> #{selectedNews.entities[0]}</span>
            )}
          </h3>
          
          <p className="preview-description">{selectedNews.text}</p>
          
          {selectedNews.why_now && (
            <div className="preview-why-now">
              <strong>Почему сейчас:</strong>
              <p>{selectedNews.why_now}</p>
            </div>
          )}

          {selectedNews.sources && selectedNews.sources.length > 0 && (
            <div className="preview-sources">
              <strong>Источники:</strong>
              <div className="sources-list">
                {selectedNews.sources.map((source, idx) => (
                  <span key={idx} className="source-tag">{source}</span>
                ))}
              </div>
            </div>
          )}

          {selectedNews.entities && selectedNews.entities.length > 0 && (
            <div className="preview-entities">
              <strong>Упоминания:</strong>
              <div className="entities-list">
                {selectedNews.entities.map((entity, idx) => (
                  <span key={idx} className="entity-tag">{entity}</span>
                ))}
              </div>
            </div>
          )}

          <div className="preview-stats">
            <div className="stat-item">
              <span className="stat-label">Горячесть:</span>
              <span className="stat-value">
                {selectedNews.hotness} <AiFillFire color="#FF6B35" size={16} />
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Тональность:</span>
              <span 
                className="stat-value"
                style={{ color: getSentimentColor(selectedNews.sentiment) }}
              >
                {getSentimentText(selectedNews.sentiment)}
              </span>
            </div>
          </div>

          <button className="copy-btn" onClick={handleCopyNews}>
            Копировать
          </button>

          {selectedNews.timeline && selectedNews.timeline.length > 0 && (
            <div className="news-meta">
              <span className="news-meta-date">
                {formatDate(selectedNews.timeline[0].date)}
              </span>
            </div>
          )}
        </div>
      ) : (
        <div className="no-selection">
          <p>Выберите новость из ленты для создания черновика</p>
        </div>
      )}

      {/* Draft Editor */}
      <div className="draft-editor">
        <h3 className="editor-title">Создание черновика</h3>
        
        <div className="editor-actions">
          <button className="editor-action-btn">Поменять тональность</button>
          <button className="editor-action-btn">Повысить температуру</button>
          <button className="editor-action-btn">Понизить</button>
        </div>

        <textarea
          className="draft-textarea"
          placeholder="Напишите что-нибудь..."
          value={draftText}
          onChange={(e) => setDraftText(e.target.value)}
        />

        <button 
          className="create-draft-btn"
          onClick={handleSubmitDraft}
        >
          Создать черновик
        </button>
      </div>
    </div>
  );
};

export default RightPanel;