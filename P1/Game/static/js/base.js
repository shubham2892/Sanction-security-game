
// Function for changing "incomplete" resources to "complete" on click
$(document).ready(function(){
    $(".resource-container.incomplete").one( "click", function(){
        console.log("click event");
        $( this ).removeClass("incomplete").addClass("complete");
    });
});

// Function for PC Health and Points vertical progress bars
$(document).ready(function(){
    var healthBar = $('.health').children().find('.inner');
    var healthVal = healthBar.attr("data-progress");
    var healthInt = parseInt(healthVal);

    // Add the appropriate color to the bar
    if (healthInt > 80) {
      healthBar.addClass("high");
    }
    else if (healthInt < 20) {
      healthBar.addClass("low");
    }
    else {
      healthBar.addClass("middle");
    }

    // Animate bar
    $(healthBar).animate({
        height: healthVal
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


// Wipe Research Objective upon completion, and replace it with a new one.
