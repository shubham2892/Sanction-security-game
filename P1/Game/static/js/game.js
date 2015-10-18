
// Function for changing "incomplete" resources to "complete" on click
$(document).ready(function(){

    // When incomplete resource is clicked...
    $(".resource-container.incomplete").one( "click", function(){

        // Change class from .incomplete to .complete
        $( this ).removeClass("incomplete").addClass("complete");

        // Remove objective if complete
        var resourceList = $( this ).closest('.resource-list');


        // If all children objects are complete, remove resource list
        if (resourceList.find(".incomplete").length === 0) {
            resourceList.find('.resource-container').fadeOut("slow", function(){
              this.remove();
            });
        }

    });
});

// Function for PC Health and Points vertical progress bars
$(document).ready(function(){

    // Get blue threat
    var blueBar = $('.attack-threat').find('.inner.blue');
    var blueThreat = blueBar.attr("blue-threat");

    // Animate bar
    $(blueBar).animate({
        height: blueThreat
    }, 1500);

     // Get blue threat
    var redBar = $('.attack-threat').find('.inner.red');
    var redThreat = parseInt(redBar.attr("red-threat")) + parseInt(blueThreat);
    var redCent = redThreat + "%";

    // Animate bar
    $(redBar).animate({
        height: redCent
    }, 1500);

    // Get blue threat
    var yellowBar = $('.attack-threat').find('.inner.yellow');
    var yellowThreat = parseInt(yellowBar.attr("yellow-threat")) + redThreat;
    var yellowCent = yellowThreat + "%";

    // Animate bar
    $(yellowBar).animate({
        height: yellowCent
    }, 1500);

});

// Player Score Horizontal Bars
$(document).ready(function() {
    $( ".progressbar" ).progressbar({
      value: 60
    });
});

// $(".progressbar").bind('progressbarchange', function(event, ui) {
//         var selector = "#" + this.id + " > div";
//         var value = this.getAttribute( "aria-valuenow" );
//         if (value < 10){
//             $(selector).css({ 'background': 'Red' });
//         } else if (value < 30){
//             $(selector).css({ 'background': 'Orange' });
//         } else if (value < 50){
//             $(selector).css({ 'background': 'Yellow' });
//         } else{
//             $(selector).css({ 'background': 'LightGreen' });
//         }
//     });



// Prompt player if s/he tries to reload page
// window.onbeforeunload = function() {
//     return "Refreshing the page during the game may lead to undesired consequences.  Please return to the page. Thanks!";
// }

