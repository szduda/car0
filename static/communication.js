// WebSocket config
const socket = new WebSocket(`ws://${location.host}/steer`)

socket.addEventListener('message', (ev) => log(ev.data, '#04f'))
socket.addEventListener('open', () => socket.send('stp') )//log('WS opened', '#4f2'))
socket.addEventListener('error', () => log('WS error', '#f8a'))
socket.addEventListener('close', () => log('WS closed'))


// EventSource config (SSE)
const sse = new EventSource(`//${location.host}/monitor`)
const sseMaxReconnections = 5
let sseReconnections = 0

sse.onopen = (ev) => {
  if (ev.target.readyState === 1) {
    log('SSE opened', '#4f2')
  }
}

sse.onclose = () => log('SSE closed')

sse.onmessage = (e) => {
  log(`SSE message: ${e.data}`, '#80f')
  const data = JSON.parse(e.data)
  document.getElementById('voltage').innerHTML = `${data.v.toFixed(2)} V  (${data.vp}%)`
  document.getElementById('current').innerHTML = `${data.c.toFixed(0)} mA  (${data.cp}%)`
  document.getElementById('batteryH').innerHTML = data.h
  document.getElementById('batteryM').innerHTML = data.m
}

sse.onerror = () => {
  sseReconnections++
  if (sseReconnections > sseMaxReconnections) {
    log('SSE error. Failed to reconnect. Closing connection.', '#a00')
    sse.close()
  } else {
    log(`SSE error. Reconnecting ${sseReconnections}/${sseMaxReconnections}`, '#f8a')
  }
}
