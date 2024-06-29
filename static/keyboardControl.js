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

let kb_speed = 0
let kb_angle = 0

const getKeyId = (key) => key === ' ' ? 'space' : key

document.onkeydown = (e) => {
  if (e.repeat) {
    return
  }

  if (e.key in speedKeyMap) {
    kb_speed = speedKeyMap[e.key]
    speedKeyMap.ArrowUp = Math.min(kb_speed + 0.1, 1.0)
    speedKeyMap.ArrowDown = Math.max(kb_speed - 0.1, 0.4)
    socket.send(`speed:${kb_speed}`)
    log(`New speed [${kb_speed}]`, '#fb0')
  }

  if (e.key in steerKeyMap) {
    const cmd = steerKeyMap[e.key]
    socket.send(cmd)
    log(`Command [${cmd}]`, '#fb0')
  }

  if (e.key in accKeys) {
    const fwd = e.key === 'w'
    if(kb_speed === 0) {
      kb_speed = 1.0
    }
    const newSpeed = fwd ? kb_speed : -kb_speed
    socket.send(`speed:${newSpeed}`)
    log(`Drive ${fwd ? 'forward' : 'backwards'} with speed: ${newSpeed}`, '#fb0')
  }

    if (e.key in turnKeys) {
    const left = e.key === 'a'
    const newAngle = left ? -0.8 : 0.8
    socket.send(`angle:${newAngle}`)
    log(`Turn ${left ? 'left' : 'right'} with speed: ${newAngle}`, '#fb0')
  }

  document.getElementById(getKeyId(e.key))?.setAttribute('data-pressed', true)
}

document.onkeyup = (e) => {
  if (e.key in accKeys) {
    socket.send('stp')
    log('Full Stop', '#fb0')
  }

  if (e.key in rotateKeys) {
      socket.send('angle:0')
      kb_angle = 0
      log('Rotate stop', '#fb0')
  }

  if (e.key in turnKeys) {
    kb_angle = 0
    socket.send('angle:0')
    log('Turn stop', '#fb0')
  }

  const el = document.getElementById(getKeyId(e.key))
  if (el) {
    el.removeAttribute('data-pressed')
  }
}
