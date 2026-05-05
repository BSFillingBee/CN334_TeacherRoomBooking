function showRoom(id) {
  document.getElementById('tooltip-' + id).style.display = 'block';
}
function hideRoom() {
  document.querySelectorAll('.room-tooltip').forEach(t => t.style.display = 'none');
}