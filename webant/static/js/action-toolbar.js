$("#delete-button").on("click", function() {
    $.ajax({ method: "DELETE", url: API_URL + "/volumes/" + $(this).data('target') })
      .done(function() {
        window.history.back();
      })
      .fail(function() {
        alert("deletion failed");
      })
      .always(function() {
        $('#confirm-deletion-modal').modal('hide');
      });
});
