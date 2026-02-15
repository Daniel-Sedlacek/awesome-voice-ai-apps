import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// McDonald's API
export const mcdonalds = {
  async getMenuItems() {
    const response = await apiClient.get('/api/mcdonalds/menu/')
    return response.data
  },
  async getCategories() {
    const response = await apiClient.get('/api/mcdonalds/menu/categories')
    return response.data
  },
  async getMenuByCategory(category) {
    const response = await apiClient.get(`/api/mcdonalds/menu/category/${category}`)
    return response.data
  },
  async addToBasket(sessionId, itemId) {
    const response = await apiClient.post('/api/mcdonalds/basket/add', {
      session_id: sessionId,
      item_id: itemId,
    })
    return response.data
  },
  async removeFromBasket(sessionId, itemId) {
    const response = await apiClient.post('/api/mcdonalds/basket/remove', {
      session_id: sessionId,
      item_id: itemId,
    })
    return response.data
  },
}

// Transport API
export const transport = {
  async processAudio(audioBase64, sourceLocale, targetLocale1, targetLocale2) {
    const response = await apiClient.post('/api/transport/process', {
      audio_base64: audioBase64,
      source_locale: sourceLocale,
      target_locale_1: targetLocale1,
      target_locale_2: targetLocale2,
    })
    return response.data
  },
  async getLanguages() {
    const response = await apiClient.get('/api/transport/languages')
    return response.data
  },
}

// Dental API
export const dental = {
  async processAudio(audioBase64, locale) {
    const response = await apiClient.post('/api/dental/process', {
      audio_base64: audioBase64,
      locale,
    })
    return response.data
  },
  async getLanguages() {
    const response = await apiClient.get('/api/dental/languages')
    return response.data
  },
}

// Psychotherapy API
export const psychotherapy = {
  async processAudio(audioBase64, locale) {
    const response = await apiClient.post('/api/psychotherapy/process', {
      audio_base64: audioBase64,
      locale,
    })
    return response.data
  },
  async getSessions() {
    const response = await apiClient.get('/api/psychotherapy/sessions')
    return response.data
  },
  async getLanguages() {
    const response = await apiClient.get('/api/psychotherapy/languages')
    return response.data
  },
}
