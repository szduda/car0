const log = (text, color) => {
  const debugOut = document.getElementById('debugOut');
  debugOut.innerHTML += `<span style="color: ${color}">${text}<br/></span>`;

  if (debugOut.children.length > 15) {
    debugOut.removeChild(debugOut.children[0])
  }
};

const socket = new WebSocket('ws://' + location.host + '/steer');
socket.addEventListener('message', ev => {
  log('<<< ' + ev.data, 'blue');
});
socket.addEventListener('close', ev => {
  log('<<< WS closed');
});

const sse = new EventSource(`//${location.host}/monitor`)
sse.onopen = () => log('>>> SSE opened')
sse.onmessage = (e) => {
  log(`>>> SSE message: ${e.data}`)
  const data = JSON.parse(e.data)
  document.getElementById('voltage').innerHTML = `${data.v.toFixed(2)} V  (${data.vp}%)`
  document.getElementById('current').innerHTML = `${data.c.toFixed(0)} mA  (${data.cp}%)`
  document.getElementById('batteryH').innerHTML = data.h
  document.getElementById('batteryM').innerHTML = data.m
}
sse.onerror = () => log('>>> SSE error; reconnecting')

document.getElementById('form').onsubmit = ev => {
  ev.preventDefault();
  const input = document.getElementById('cmdInput');
  log('>>> ' + input.value, 'red');
  socket.send(input.value);
  input.value = '';
};
