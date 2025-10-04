// Определение тональности на основе числа
export const getSentimentLabel = (sentiment) => {
    if (sentiment > 0.3) return 'positive';
    if (sentiment < -0.3) return 'negative';
    return 'neutral';
  };
  
  export const getSentimentColor = (sentiment) => {
    const label = getSentimentLabel(sentiment);
    switch (label) {
      case 'positive':
        return '#4CAF50';
      case 'negative':
        return '#F44336';
      default:
        return '#FF9800';
    }
  };
  
  export const getSentimentText = (sentiment) => {
    const label = getSentimentLabel(sentiment);
    switch (label) {
      case 'positive':
        return 'Позитив';
      case 'negative':
        return 'Негатив';
      default:
        return 'Нейтрал';
    }
  };
  
  // Определение "горячести" новости
  export const isHotNews = (hotness) => {
    return hotness >= 60; // Новость считается горячей если hotness >= 60
  };
  
  // Форматирование даты
  export const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'numeric',
      year: 'numeric'
    });
  };
  
  // Извлечение тикеров из entities
  export const extractTickers = (entities) => {
    if (!entities || !Array.isArray(entities)) return [];
    // Можно добавить логику для определения тикеров
    return entities.filter(e => e.startsWith('$') || e.match(/^[A-Z]{2,5}$/));
  };