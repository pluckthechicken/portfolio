// Functions for interacting with positions

const closePositionPrompt = (id, name) => {
  console.log(`Prompting position close for id=${id}`);
  $('#modal-close .modal-body p.lead').text(
    `Close position for ${name}?`
  );
  $('#modal-close input[type="hidden"]').val(id);
}

const resetModal = () => {
  $('#modal-close .modal-body p.lead').text('');
  $('#modal-close input[type="hidden"]').val('');
}
