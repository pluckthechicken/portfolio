// Functions for interacting with positions

const closePositionPrompt = (id, name) => {
  $('#modal-close-title').text(`Close position for ${name}?`);
  $('#modal-close input[type="hidden"]').val(id);
}

const resetCloseModal = () => {
  $('#modal-close-title').text('');
  $('#modal-close input[type="hidden"]').val('');
}
