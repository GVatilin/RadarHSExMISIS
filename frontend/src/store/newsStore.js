import { create } from 'zustand';
import { newsAPI } from '../services/api';

export const useNewsStore = create((set, get) => ({
  news: [],
  selectedNews: null,
  loading: false,
  error: null,
  viewMode: 'all', // 'all' или 'hot'
  hotNewsHours: 24,
  
  filters: {
    search: '',
    category: null,
    company: null,
    priceChange: null,
    sector: null,
    sentiment: null,
    source: null,
    sortBy: 'hottest'
  },
  
  // Загрузить все новости
  fetchAllNews: async () => {
    set({ loading: true, error: null, viewMode: 'all' });
    try {
      const data = await newsAPI.getAllNews();
      set({ news: data.news || [], loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  // Загрузить горячие новости
  fetchHotNews: async (hours = 24) => {
    set({ loading: true, error: null, viewMode: 'hot', hotNewsHours: hours });
    try {
      const data = await newsAPI.getHotNews(hours);
      set({ news: data.news || [], loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  setSelectedNews: (news) => set({ selectedNews: news }),
  
  setFilter: (filterName, value) => set((state) => ({
    filters: {
      ...state.filters,
      [filterName]: value
    }
  })),
  
  clearFilters: () => set({
    filters: {
      search: '',
      category: null,
      company: null,
      priceChange: null,
      sector: null,
      sentiment: null,
      source: null,
      sortBy: 'hottest'
    }
  }),
  
  // Получить отфильтрованные новости
  getFilteredNews: () => {
    const { news, filters } = get();
    let filtered = [...news];
    
    // Фильтр по поиску
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(item => 
        item.headline?.toLowerCase().includes(searchLower) ||
        item.text?.toLowerCase().includes(searchLower)
      );
    }
    
    // Фильтр по тональности
    if (filters.sentiment !== null && filters.sentiment !== 'all') {
      filtered = filtered.filter(item => {
        const sentimentLabel = getSentimentLabel(item.sentiment);
        return sentimentLabel === filters.sentiment;
      });
    }
    
    // Фильтр по источнику
    if (filters.source && filters.source !== 'all') {
      filtered = filtered.filter(item => 
        item.sources?.includes(filters.source)
      );
    }
    
    // Сортировка
    if (filters.sortBy === 'hottest') {
      filtered.sort((a, b) => (b.hotness || 0) - (a.hotness || 0));
    } else if (filters.sortBy === 'recent') {
      filtered.sort((a, b) => {
        const dateA = a.timeline?.[0]?.date || 0;
        const dateB = b.timeline?.[0]?.date || 0;
        return new Date(dateB) - new Date(dateA);
      });
    }
    
    return filtered;
  }
}));

// Вспомогательная функция для определения тональности
const getSentimentLabel = (sentiment) => {
  if (sentiment > 0.3) return 'positive';
  if (sentiment < -0.3) return 'negative';
  return 'neutral';
};