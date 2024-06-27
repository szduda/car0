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
  ArrowUp: 0.6,
  ArrowDown: 0.4,
  3: 0.3,
  4: 0.4,
  5: 0.5,
  6: 0.6,
  7: 0.7,
  8: 0.8,
  9: 0.9,
}

const steerKeyMap = {
  Escape: 'bye',
  q: 'rtl',
  e: 'rtr',
  ' ': 'stp',
}

const accKeys = {w: true, s: true}
const rotateKeys = {q: true, e: true}
const turnKeys = {a: true, d: true}

let speed = 0
let angle = 0

const getKeyId = (key) => key === ' ' ? 'space' : key

document.onkeydown = (e) => {
  if (e.repeat) {
    return
  }

  if (e.key in speedKeyMap) {
    speed = speedKeyMap[e.key]
    speedKeyMap.ArrowUp = Math.min(speed + 0.1, 1.0)
    speedKeyMap.ArrowDown = Math.max(speed - 0.1, 0.4)
    socket.send(`speed:${speed}`)
    log(`New speed [${speed}]`, '#fb0')
  }

  if (e.key in steerKeyMap) {
    const cmd = steerKeyMap[e.key]
    socket.send(cmd)
    log(`Command [${cmd}]`, '#fb0')
  }

  if (e.key in accKeys) {
    const fwd = e.key === 'w'
    if(speed === 0) {
      speed = 0.9
    }
    const newSpeed = fwd ? speed : -speed
    socket.send(`speed:${newSpeed}`)
    log(`Drive ${fwd ? 'forward' : 'backwards'} with speed: ${newSpeed}`, '#fb0')
  }

    if (e.key in turnKeys) {
    const left = e.key === 'a'
    const newAngle = left ? -0.2 : 0.2
    socket.send(`angle:${newAngle}`)
    log(`Turn ${left ? 'left' : 'right'} with speed: ${newAngle}`, '#fb0')
  }

  document.getElementById(getKeyId(e.key))?.setAttribute('data-pressed', true)
}

document.onkeyup = (e) => {
  if (e.key in accKeys) {
    socket.send('stp')
    log('Stop', '#fb0')
  }

  if (e.key in rotateKeys) {
      socket.send('angle:0')
      angle = 0
      log('Stop', '#fb0')
  }

  if (e.key in turnKeys) {
    angle = 0
    socket.send('angle:0')
    log('Go straight', '#fb0')
  }

  const el = document.getElementById(getKeyId(e.key))
  if (el) {
    el.removeAttribute('data-pressed')
  }
}

document.getElementById('debugOutToggle').onclick = () => {
  const debugOut = document.getElementById('debugOut');
  debugOut.classList.toggle('hidden')
}
