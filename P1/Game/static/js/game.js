
// Function for changing "incomplete" research resources to "complete" on click
$(function(){

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

// Function for changing "incomplete" security vulnerabilities to "complete" on click
$(function(){

    // When incomplete resource is clicked...
    $(".resource-container.vulnerable").one( "click", function(){

        // Change class from .incomplete to .complete
        $( this ).removeClass("vulnerable").addClass("capable");
        $()

        // Remove objective if complete
        var resourceList = $( this ).closest('.resource-list');

    });
});

// Function for Attack Threat vertical bar
$(function(){

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

// Player Score Horizontal Bars, needs to be normalized to highest score
// Maybe change to Bootstrap progress bar?
$(function() {

    var table = document.getElementById("player-info");
    for (var i = 0, row; row = table.rows[i]; i++) {
        var score = parseInt($('tr#score').attr("player-score"));
        var progressbar = (".progressbar." + (i + 1).toString());
        console.log(progressbar);
        $( progressbar ).progressbar({
             value: score
        });
    }
});


$(function() {
        $(".panel-body.chat").scrollTop($(".panel-body.chat")[0].scrollHeight);
});

