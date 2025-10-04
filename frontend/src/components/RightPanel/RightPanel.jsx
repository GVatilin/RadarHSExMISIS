import React, { useState } from 'react';
import { BiPencil } from 'react-icons/bi';
import { AiOutlineSmile, AiOutlineLike, AiFillFire } from 'react-icons/ai';
import { BsGraphUp } from 'react-icons/bs';
import { useNewsStore } from '../../store/newsStore';
import './RightPanel.css';

const RightPanel = () => {
  const [draftText, setDraftText] = useState('');
  const selectedNews = useNewsStore((state) => state.selectedNews);

  const handleSubmitDraft = () => {
    console.log('Draft submitted:', draftText);
    // Здесь будет отправка на бэкенд
    alert('Черновик создан!');
    setDraftText('');
  };


  const copyContentToClipboard = () => {
    const title = document.querySelector('.preview-title').innerText;
    const description = document.querySelector('.preview-description').innerText;
    const contentToCopy = `${title}\n${description}`;
    
    navigator.clipboard.writeText(contentToCopy)
      .then(() => {
        console.log('Содержимое скопировано в буфер обмена');
      })
      .catch(err => {
        console.error('Ошибка при копировании содержимого: ', err);
      });
  };







  return (
    <div className="right-panel">
      {/* Header */}
      <div className="assistant-header">
        <BiPencil size={24} color="#9C27B0" />
        <h2 className="assistant-title">Ассистент</h2>
      </div>

      {/* Selected News Preview */}
      {selectedNews && (
        <div className="selected-news-preview">
          <h3 className="preview-title">
            {selectedNews.title.split('#')[0]}
            <span className="preview-ticker">#{selectedNews.company}</span>
            {selectedNews.title.split('#')[1]?.replace(selectedNews.company, '')}
          </h3>
          <p className="preview-description">{selectedNews.description}</p>
          
          <button className="preview-link">Статья →</button>

          <div className="preview-reactions">
            {/*<span className="reaction-item">
              {selectedNews.reactions.smile} <AiOutlineSmile size={18} />
            </span>*/}
            <span className="reaction-item">
              {selectedNews.reactions.thumbsUp} <AiOutlineLike size={18} />
            </span>
            {/*<span className="reaction-item">
              {selectedNews.reactions.fire} <AiFillFire size={18} />
            </span>*/}
            <span className="reaction-item">
              {selectedNews.reactions.chart} <BsGraphUp size={18} />
            </span>
          </div>

          <button className="copy-btn" onClick={copyContentToClipboard}>Копировать</button>

          <div className="news-meta">
            <span className="news-meta-date">{selectedNews.date}</span>
          </div>
        </div>
      )}

      {/* Draft Editor */}
      <div className="draft-editor">
        <div className="editor-actions">
          <button className="editor-action-btn">Повысить тон</button>
          <button className="editor-action-btn">Понизить тон</button>
          <button className="editor-action-btn">Повысить темп.</button>
          <button className="editor-action-btn">Понизить темп.</button>
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