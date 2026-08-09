const API_BASE = 'https://repo-mind-71fe.onrender.com/api/v1'

export async function cloneRepo(gitUrl, githubToken = null) {
  const res = await fetch(`${API_BASE}/repo/clone`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ git_url: gitUrl, github_token: githubToken }),
  })
  if (!res.ok) {
  const errorData = await res.json().catch(() => null);

  const message =
    errorData?.detail?.[0]?.msg ||
    errorData?.detail ||
    errorData?.message ||
    `Request failed with status ${res.status}`;

  throw new Error(message);
}

  return res.json();

}  

export async function uploadZip(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/repo/upload-zip`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error('Failed to upload zip')
  return res.json()
}

export async function listProjects() {
  const res = await fetch(`${API_BASE}/repo/list`)
  if (!res.ok) throw new Error('Failed to list projects')
  return res.json()
}

export async function getProjectSummary(projectId) {
  const res = await fetch(`${API_BASE}/repo/${projectId}/summary`)
  if (!res.ok) throw new Error('Failed to get project summary')
  return res.json()
}

export async function deleteProject(projectId) {
  const res = await fetch(`${API_BASE}/repo/${projectId}`, {
    method: 'DELETE',
  })
  if (!res.ok) throw new Error('Failed to delete project')
  return res.json()
}

export async function askQuestion(projectId, question) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, question }),
  })
  if (!res.ok) throw new Error('Failed to ask question')
  return res.json()
}

export async function askQuestionStream(projectId, question, onChunk, onDone, onError) {
  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId, question }),
    })
    
    if (!res.ok) {
      throw new Error('Stream request failed')
    }
    
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()
      
      let currentEvent = null
      
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.substring(7).trim()
        } else if (line.startsWith('data: ')) {
          const dataStr = line.substring(6).trim()
          if (!dataStr) continue
          
          try {
            const data = JSON.parse(dataStr)
            if (currentEvent === 'chunk') {
              onChunk(data)
            } else if (currentEvent === 'done') {
              onDone(data)
            } else if (currentEvent === 'error') {
              onError(data.error)
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e, dataStr)
          }
        }
      }
    }
  } catch (err) {
    onError(err.message)
  }
}

export async function getChatHistory(projectId) {
  const res = await fetch(`${API_BASE}/chat/${projectId}/history`)
  if (!res.ok) throw new Error('Failed to get chat history')
  return res.json()
}
