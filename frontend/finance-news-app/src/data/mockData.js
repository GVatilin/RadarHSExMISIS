export const mockNews = [
    {
      id: 1,
      title: 'Tesla #TSLA сообщила о росте продаж на 12%',
      description: 'Forem ipsum dolor sit amet, consectetur adipiscing elit. Nunc vulputate libero et velit interdum, ac aliquet odio mattis.',
      hotness: 67,
      isHot: true,
      sentiment: 'positive',
      source: 'Источник',
      date: '3.10.2025',
      company: 'TSLA',
      sector: 'IT',
      reactions: {
        smile: 10,
        thumbsUp: 10,
        fire: 10,
        chart: 10
      }
    },
    {
      id: 2,
      title: 'Tesla #TSLA сообщила о росте продаж на 12%',
      description: 'Forem ipsum dolor sit amet, consectetur adipiscing elit. Nunc vulputate libero et velit interdum, ac aliquet odio mattis.',
      hotness: 67,
      isHot: true,
      sentiment: 'neutral',
      source: 'Источник',
      date: '3.10.2025',
      company: 'TSLA',
      sector: 'IT',
      reactions: {
        smile: 10,
        thumbsUp: 10,
        fire: 10,
        chart: 10
      }
    },
    {
      id: 3,
      title: 'Tesla #TSLA сообщила о падении продаж на -12%',
      description: 'Forem ipsum dolor sit amet, consectetur adipiscing elit. Nunc vulputate libero et velit interdum, ac aliquet odio mattis. Forem ipsum dolor sit amet, consectetur adipiscing elit. Nunc vulputate libero et velit interdum, ac aliquet odio mattis.',
      hotness: 67,
      isHot: true,
      sentiment: 'negative',
      source: 'Источник',
      date: '3.10.2025',
      company: 'TSLA',
      sector: 'IT',
      reactions: {
        smile: 10,
        thumbsUp: 10,
        fire: 10,
        chart: 10
      }
    },
    {
      id: 4,
      title: 'Сбер #SBER показал рекордные результаты',
      description: 'Forem ipsum dolor sit amet, consectetur adipiscing elit. Nunc vulputate libero et velit interdum.',
      hotness: 45,
      isHot: false,
      sentiment: 'positive',
      source: 'Источник',
      date: '2.10.2025',
      company: 'SBER',
      sector: 'Нефть',
      reactions: {
        smile: 5,
        thumbsUp: 8,
        fire: 6,
        chart: 7
      }
    }
  ];
  
  export const mockCompanies = [
    { ticker: 'SBER', name: 'Сбер', hotness: 7 },
    { ticker: 'SBER', name: 'Сбер', hotness: 7 },
    { ticker: 'SBER', name: 'Сбер', hotness: 7 },
    { ticker: 'SBER', name: 'Сбер', hotness: 7 }
  ];
  
  export const categories = [
    'Акции',
    'Валюта',
    'Фонды',
    'Облигации',
    'Индексы'
  ];
  
  export const priceChanges = [
    { icon: '📈', label: 'Рост' },
    { icon: '📉', label: 'Падение' },
    { icon: '📊', label: 'Коррекция' }
  ];
  
  export const sectors = [
    { icon: '💻', label: 'IT' },
    { icon: '🛢️', label: 'Нефть' },
    { icon: '🛒', label: 'E-com' },
    { icon: '🏪', label: 'Ретейл' },
    { icon: '⚙️', label: 'Металлургия' },
    { icon: '🌾', label: 'Агро-пром' }
  ];