import { create } from 'zustand';
import { mockNews } from '../data/mockData';

export const useNewsStore = create((set) => ({
  news: mockNews,
  selectedNews: null,
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
  
  getFilteredNews: () => {
    // Логика фильтрации будет применяться в компоненте
    return mockNews;
  }
}));