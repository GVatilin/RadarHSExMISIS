import axios from 'axios';

const API_BASE_URL = 'http://localhost/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const newsAPI = {
  // Получить все новости
  getAllNews: async () => {
    try {
      const response = await api.get('/news/get_all_news');
      return response.data;
    } catch (error) {
      console.error('Error fetching all news:', error);
      throw error;
    }
  },

  // Получить топ-5 горячих новостей
  getHotNews: async (hours = 24) => {
    try {
      const response = await api.get('/news/get_report', {
        params: { hours }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching hot news:', error);
      throw error;
    }
  },
};

export default api;