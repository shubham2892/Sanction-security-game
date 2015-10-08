
// Function for changing "incomplete" resources to "complete" on click
$(document).ready(function(){
    $(".resource-container.incomplete").one( "click", function(){
        console.log("click event");
        $( this ).removeClass("incomplete").addClass("complete");
    });
});

// Function for PC Health and Points vertical progress bars
$(document).ready(function(){
    var skillBar = $('.health').children().find('.inner');
    var skillVal = skillBar.attr("data-progress");
    $(skillBar).animate({
        height: skillVal
    }, 1500);
});
