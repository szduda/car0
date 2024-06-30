const touchArea = document.getElementById('touchArea')
const TOUCH_THRESHOLD = 0.2
const TOUCH_STEP = 15
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

let lastSpeed = 0;
let lastAngle = 0;

const stop = () => {
  socket.send('stp')
  log('Stop')
}

const goFullscreen = (elem = document.body) => {
  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if (elem.webkitRequestFullscreen) { /* Safari */
    elem.webkitRequestFullscreen();
  }
}

function canvas_arrow(context, fromx, fromy, tox, toy, r){
	var x_center = tox;
	var y_center = toy;

	var angle;
	var x;
	var y;

	context.beginPath();

	angle = Math.atan2(toy-fromy,tox-fromx)
	x = r*Math.cos(angle) + x_center;
	y = r*Math.sin(angle) + y_center;

	context.moveTo(x, y);

	angle += (1/3)*(2*Math.PI)
	x = r*Math.cos(angle) + x_center;
	y = r*Math.sin(angle) + y_center;

	context.lineTo(x, y);

	angle += (1/3)*(2*Math.PI)
	x = r*Math.cos(angle) + x_center;
	y = r*Math.sin(angle) + y_center;

	context.lineTo(x, y);

	context.closePath();

	context.fill();
}

const ctx = touchArea.getContext("2d");

const drawAxes = (x=0, y=0) => {
  const W = touchArea.width
  const H = touchArea.height
  ctx.clearRect(0, 0, W, H);
  ctx.beginPath();
  ctx.moveTo(150+x, 50+y);
  ctx.lineTo(150+x, 250+y);
  ctx.moveTo(50+x, 150+y);
  ctx.lineTo(250+x, 150+y);
  ctx.lineWidth = 2
  ctx.strokeStyle = '#fff';
  ctx.stroke();

  ctx.fillStyle = '#fff'
  canvas_arrow(ctx, 250+x, 150+y, 280+x, 150+y, 20)
  canvas_arrow(ctx, 150+x, 250+y, 150+x, 280+y, 20)
  canvas_arrow(ctx, 50+x, 150+y, 20+x, 150+y, 20)
  canvas_arrow(ctx, 150+x, 50+y, 150+x, 20+y, 20)
}

drawAxes()

touchArea.addEventListener('touchstart', e => {
  e.preventDefault()
  goFullscreen()
  const { x, y } = getCoords(e.changedTouches[0])
  firstTouch.x = x
  firstTouch.y = y
  lastTouch.x = x
  lastTouch.y = y

  drawAxes(x,y)

  console.log('touchstart at x,y:', x, y)
}, {passive: false})

touchArea.addEventListener('touchend', e => {
  e.preventDefault()
  stop()
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

    if (speed !== lastSpeed) {
      socket.send(`speed:${speed}`)
      lastSpeed = speed
    }

    if (angle !== lastAngle) {
      socket.send(`angle:${angle}`)
      lastAngle = angle
    }

    log(`touchmove go with speed=${speed}, angle=${angle}`)
  }
}
const debouncedOnTouchMove = throttle(onTouchMove, 16)
touchArea.addEventListener('touchmove', debouncedOnTouchMove, {passive: false})

// ROTATE
const rotate = (dir) => (e) => {
  const left = dir === 'left'
  socket.send(left ? 'rtl' : 'rtr')
}
document.getElementById('rotateLeft').addEventListener('touchstart', rotate('left'))
document.getElementById('rotateLeft').addEventListener('touchend', stop)
document.getElementById('rotateRight').addEventListener('touchstart', rotate('right'))
document.getElementById('rotateRight').addEventListener('touchend', stop)
