const log = (text, color) => {
  const timestamp = new Date().toISOString().substr(11,8)
  const debugOut = document.getElementById('debugOut')
  debugOut.innerHTML += `<span><span style="color: ${color}">${timestamp}:&nbsp;</span><span style="color: ${color}">${text}</span><br/></span>`

  if (debugOut.children.length > 15) {
    debugOut.removeChild(debugOut.children[0])
  }
}

const socket = new WebSocket(`ws://${location.host}/steer`)
socket.addEventListener('message', (ev) => log(ev.data, 'blue'))
socket.addEventListener('open', () => log('WS opened'))
socket.addEventListener('error', () => log('WS error'))
socket.addEventListener('close', () => log('WS closed'))

cosnt sseMaxReconnections = 5
let sseReconnections = 0
const sse = new EventSource(`//${location.host}/monitor`)
sse.onopen = () => log('SSE opened')
sse.onmessage = (e) => {
  log(`SSE message: ${e.data}`)
  const data = JSON.parse(e.data)
  document.getElementById('voltage').innerHTML = `${data.v.toFixed(2)} V  (${data.vp}%)`
  document.getElementById('current').innerHTML = `${data.c.toFixed(0)} mA  (${data.cp}%)`
  document.getElementById('batteryH').innerHTML = data.h
  document.getElementById('batteryM').innerHTML = data.m
}
sse.onerror = () => {
  sseReconnections++
  if(sseReconnections > sseMaxReconnections) {
    log('SSE error. Failed to reconnect. Closing connection.')
    sse.close()
  }

  log(`SSE error. Reconnecting ${sseReconnections}/${sseMaxReconnections}`)
}

document.getElementById('form').onsubmit = ev => {
  ev.preventDefault()
  const input = document.getElementById('cmdInput')
  log(input.value, 'red')
  socket.send(input.value)
  input.value = ''
}
