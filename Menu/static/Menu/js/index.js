var $a = $('h4');
$a.on('click', function(event) {
  var date = new Date(event.timeStamp);
    console.log("You clicked on: " + date)
});