
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

// Handle for in-game changes to PC Health

// $('.inner').attr("data-progress").change(function(){
//     alert( "Handler for .change() called." );
//     var healthBar = $('.health').children().find('.inner');
//     var healthVal = healthBar.attr("data-progress");
//     var healthInt = parseInt(healthVal);

//     // Add the appropriate color to the bar
//     if (healthInt > 80) {
//       healthBar.addClass("high");
//     }
//     else if (healthInt < 20) {
//       healthBar.addClass("low");
//     }
//     else {
//       healthBar.addClass("middle");
//     }

//     // Animate bar
//     $(healthBar).animate({
//         height: healthVal
//     }, 1500);
// });

// Prompt player if s/he tries to reload page
window.onbeforeunload = function() {
    return "Refreshing the page during the game may lead to undesired consequences.  Please return to the page. Thanks!";
}

