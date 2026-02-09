import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function processAudio(audioBlob, sessionId = null, language = 'en-US') {
  const base64 = await blobToBase64(audioBlob)
  const response = await apiClient.post('/process-audio', {
    audio_base64: base64,
    session_id: sessionId,
    language: language,
  })
  return response.data
}

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

async function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}
