var $pdf = $('#choose_pdf');
var $text = $('#choose_text');

$( "#pdf_form" ).hide()

$pdf.on('click', function(event) {
    $( "#text_form" ).hide(200)
    $( "#pdf_form" ).show(200)
});

$text.on('click', function(event) {
    $( "#text_form" ).show(200)
    $( "#pdf_form" ).hide(200)
  });