const log = (text, color = 'inherit') => {
  const timestamp = new Date().toISOString().substr(11, 8)
  const debugOut = document.getElementById('debugOut')
  debugOut.innerHTML += `<span><span style="opacity: 0.4">${timestamp}:&nbsp;</span><span style="color: ${color}">${text}</span><br/></span>`

  if (debugOut.children.length > 15) {
    debugOut.removeChild(debugOut.children[0])
  }
}


// WebSocket config
const socket = new WebSocket(`ws://${location.host}/steer`)

socket.addEventListener('message', (ev) => log(ev.data, '#04f'))
socket.addEventListener('open', () => log('WS opened', '#4f2'))
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


// User interactions
const speedKeyMap = {
  ArrowUp: 6,
  ArrowDown: 4,
  3: 3,
  4: 4,
  5: 5,
  6: 6,
  7: 7,
  8: 8,
  9: 9,
}

const steerKeyMap = {
  Escape: 'bye',
  w: 'fwd',
  s: 'rev',
  a: 'rtl',
  d: 'rtr',
  ' ': 'stp',
}

const getKeyId = (key) => key === ' ' ? 'space' : key

document.onkeydown = (e) => {
  if (e.repeat) {
    return
  }

  if (e.key in speedKeyMap) {
    const speed = speedKeyMap[e.key]
    speedKeyMap.ArrowUp = Math.min(speed + 1, 9)
    speedKeyMap.ArrowDown = Math.max(speed - 1, 3)
    socket.send(String(speed))
    log(`New speed [${speed}]`, '#fb0')
  }

  if (e.key in steerKeyMap) {
    const cmd = steerKeyMap[e.key]
    socket.send(cmd)
    log(`New command [${cmd}]`, '#fb0')
  }

  document.getElementById(getKeyId(e.key))?.setAttribute('data-pressed', true)
}

document.onkeyup = (e) => {
  const el = document.getElementById(getKeyId(e.key))
  if (!el) {
    return
  }

  socket.send('stp')
  log('Sending [stp] due to key release', '#fb0')
  el.removeAttribute('data-pressed')
}
