const log = (text, color) => {
  document.getElementById('debugOut').innerHTML += `<span style="color: ${color}">${text}</span><br/>`;
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
  document.getElementById('voltage').innerHTML = data.voltage
}
sse.onerror = () => log('>>> SSE error; reconnecting')

document.getElementById('form').onsubmit = ev => {
  ev.preventDefault();
  const input = document.getElementById('cmdInput');
  log('>>> ' + input.value, 'red');
  socket.send(input.value);
  input.value = '';
};