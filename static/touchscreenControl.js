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

const clearCanvas = () => {
  const W = touchArea.width
  const H = touchArea.height
  ctx.clearRect(0, 0, W, H);
}

const drawAxes = (x=150, y=150) => {
  clearCanvas();
  ctx.beginPath();
  ctx.moveTo(x, y+50);
  ctx.lineTo(x, y-50);
  ctx.moveTo(x-50, y);
  ctx.lineTo(x+50, y);
  ctx.lineWidth = 2
  ctx.strokeStyle = '#fff';
  ctx.stroke();

  ctx.fillStyle = '#fff'
  canvas_arrow(ctx, x, y+50, x, y+80, 20)
  canvas_arrow(ctx, x, y-50, x, y-80, 20)
  canvas_arrow(ctx, x-50, y, x-80, y, 20)
  canvas_arrow(ctx, x+50, y, x+80, y, 20)
}
drawAxes()

const drawLine = (x,y,xx,yy, color='#00F') => {
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(xxx, yy)
  ctx.strokeStyle = color
  ctx.stroke()
}

const drawResultant = () => {
  const [dX,dY] = getInteractionLocation(lastTouch)
  drawLine(cY, touchArea.width - cX, dY, touchArea.width - dX)
}

function getInteractionLocation(pos) {
    const rect = touchArea.getBoundingClientRect()
    const x_rel = pos.x - rect.left
    const y_rel = pos.y - rect.top
    const x = Math.round((x_rel * touchArea.width) / rect.width)
    const y = Math.round((y_rel * touchArea.height) / rect.height)
    return [x, y]
};

const drawFirstTouchAxes = () => {
  const [cX,cY] = getInteractionLocation(firstTouch)
  console.log('canvas x,y', cY,touchArea.width - cX)
  drawAxes(cY,touchArea.width - cX)
}

touchArea.addEventListener('touchstart', e => {
  e.preventDefault()

  goFullscreen()
  const { x, y } = getCoords(e.changedTouches[0])
  firstTouch.x = x
  firstTouch.y = y
  lastTouch.x = x
  lastTouch.y = y

  drawFirstTouchAxes()

  console.log('touchstart at x,y:', x, y)
}, {passive: false})

touchArea.addEventListener('touchend', e => {
  clearCanvas();
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

    clearCanvas()
    drawFirstTouchAxes()
    drawResultant()

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
