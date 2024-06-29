const touchArea = document.getElementById('touchArea')
const TOUCH_THRESHOLD = 0.3
const TOUCH_STEP = 20
const getCoords = ({pageX, pageY}) => ({
  x: Math.round(pageX / TOUCH_STEP) * TOUCH_STEP,
  y: Math.round(pageY / TOUCH_STEP) * TOUCH_STEP
})
const firstTouch = {
  x: -1,
  y: -1,
}
const lastTouch = {
  x: -1,
  y: -1,
}

touchArea.addEventListener('touchstart', e => {
  e.preventDefault()
  log('Touch start')
  const { x, y } = getCoords(e.changedTouches[0])
  firstTouch.x = x
  firstTouch.y = y
  lastTouch.x = x
  lastTouch.y = y
  console.log('touchstart at x,y:', x, y)
}, {passive: false})

touchArea.addEventListener('touchend', e => {
  e.preventDefault()
  console.log('touchend')
}, {passive: false})

const normalize = value => {
  const normal = Math.max(-1, Math.min(1, value / 10.0))
  if (Math.abs(normal) >= TOUCH_THRESHOLD) {
    return normal
  }
  return 0
}

const getDriveParams = () => ({
  speed: normalize((lastTouch.x - firstTouch.x) / TOUCH_STEP),
  angle: normalize((lastTouch.y - firstTouch.y) / TOUCH_STEP)
})

const onTouchMove = e => {
  e.preventDefault()
  const { x, y } = getCoords(e.changedTouches[0])
  if (x !== lastTouch.x || y !== lastTouch.y) {
    lastTouch.x = x
    lastTouch.y = y
    const { speed, angle } = getDriveParams()

    socket.send(`speed:${speed}`)
    socket.send(`angle:${angle}`)
    console.log('touchmove go with speed =', speed, 'angle =', angle)
  }
}
const debouncedOnTouchMove = throttle(onTouchMove, 16)
touchArea.addEventListener('touchmove', debouncedOnTouchMove, {passive: false})

const stop = () => {
  socket.send('stp')
}
document.getElementById('stopButton').addEventListener('click', stop)
