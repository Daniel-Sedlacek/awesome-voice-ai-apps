import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function getMenuItems() {
  const response = await apiClient.get('/menu/')
  return response.data
}

export async function getCategories() {
  const response = await apiClient.get('/menu/categories')
  return response.data
}

export async function getMenuByCategory(category) {
  const response = await apiClient.get(`/menu/category/${category}`)
  return response.data
}

export async function addToBasket(sessionId, itemId) {
  const response = await apiClient.post('/basket/add', {
    session_id: sessionId,
    item_id: itemId,
  })
  return response.data
}

export async function removeFromBasket(sessionId, itemId) {
  const response = await apiClient.post('/basket/remove', {
    session_id: sessionId,
    item_id: itemId,
  })
  return response.data
}


