const log = (text, color = 'inherit') => {
  const timestamp = new Date().toISOString().substr(11, 8)
  const debugOut = document.getElementById('debugOut')
  debugOut.innerHTML += `<span><span style="opacity: 0.4">${timestamp}:&nbsp;</span><span style="color: ${color}">${text}</span><br/></span>`

  if (debugOut.children.length > 15) {
    debugOut.removeChild(debugOut.children[0])
  }
}

const toggleDebug = () => {
  const debugOut = document.getElementById('debugOut');
  debugOut.classList.toggle('hidden')
  return !debugOut.classList.contains('hidden');
}

const debug = localStorage.getItem('debug') === 'true'
if (debug === document.getElementById('debugOut').classList.contains('hidden')) {
  toggleDebug()
}

document.getElementById('debugOutToggle').onclick = () => {
  const visible = toggleDebug()
  localStorage.setItem('debug', visible)
}
