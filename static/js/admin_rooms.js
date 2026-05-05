function openEditModal(id, code, name, capacity, type) {
  document.getElementById('editRoomCode').textContent = code;
  document.getElementById('editRoomName').value = name;
  document.getElementById('editRoomCap').value = capacity;
  document.getElementById('editRoomType').value = type;
  document.getElementById('editRoomForm').action = '/admin-panel/rooms/' + id + '/edit/';
  document.getElementById('editRoomModal').style.display = 'flex';
}