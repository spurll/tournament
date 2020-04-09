function resize() {
  if ($(window).width() < 700) {
    $('body').addClass('small-screen');
  }
  else {
    $('body').removeClass('small-screen');
  }

  // Resizes the title buffer which pushes content down below the floating title bar
  $('#title-buffer').height($('#title-bar').outerHeight());
}

$(document).ready(resize);
$(window).resize(resize);
$(window).on('orientationchange', resize);

