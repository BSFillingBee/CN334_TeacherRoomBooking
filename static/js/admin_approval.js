function openRejectModal(bookingId) {
  document.getElementById('rejectForm').action = '/admin-panel/bookings/' + bookingId + '/review/';
  const modal = document.getElementById('rejectModal');
  modal.style.display = 'flex';
  modal.style.alignItems = 'flex-start';
  modal.style.paddingTop = window.scrollY + 80 + 'px';
}