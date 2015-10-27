
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

//Player Score Horizontal Bars
$(function() {
    var table = document.getElementById("player-info");
    for (var i = 0, row; row = table.rows[i]; i++) {
        var progressbar = $(".progress-bar." + i);
        var score = parseInt(progressbar.attr("aria-valuenow"));
        if(score > 80) {
            progressbar.addClass("progress-bar-success");
        } else if (score > 20) {
            progressbar.addClass("progress-bar-warning");
        } else {
            progressbar.addClass("progress-bar-danger");
        }
    }
});

$(function() {
    scrollChat();
});

// AJAX POST message for game chat
$('#message-form').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!")  // sanity check
    create_message();
});

function create_message() {
    console.log("create message is working!") // sanity check
    $.ajax({
        url : "/message/create/", // the endpoint
        type : "POST", // http method
        data : { the_message : $('#id_content').val() }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $('#id_content').val(''); // remove the value from the input
            updateChat();
            console.log(json); // log the returned json to the console
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

// Keeps chat scrolled to the bottom
function scrollChat() {
        var chatWindow = $(".panel-body.chat");
        $(chatWindow).animate({scrollTop:$(chatWindow)[0].scrollHeight}, 1000);
};

function updateChat(){
    $("#talk").load(document.URL +  ' #talk');
    scrollChat();
}

// setInterval("updateChat()",1000);  //call updateChat() function every 1 seconds


// AJAX POST activate security resource
$(document).on('click', '.clickable.inactive',function(event){
    var clicked_resource = $(this);
    // Change class from .inactive to .active
    clicked_resource.removeClass("inactive").addClass("active");
    event.preventDefault();
    console.log("resource clicked");  // sanity check
    var color = clicked_resource.attr('id');
    activate_security_resource(clicked_resource);
});

function activate_security_resource(clicked_resource) {
    console.log("Security Resource Activated!") // sanity check
    $.ajax({
        url : "/resource/activate/", // the endpoint
        type : "POST", // http method
        data : { pk : $(clicked_resource).attr('value') }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $("#vulnerabilities").load(location.href +" #vulnerabilities>*","");
            console.log(json); // log the returned json to the console
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

// AJAX POST complete research resource
$(document).on('click', '.clickable.incomplete', function(event){
    var clicked_resource = $(this);
    // Change class from .incomplete to .complete
    clicked_resource.removeClass("incomplete").addClass("complete");
    event.preventDefault();
    console.log("resource clicked");  // sanity check
    var color = clicked_resource.attr('id');
    complete_research_resource(clicked_resource);
});

function complete_research_resource(clicked_resource) {
    console.log("Research Resource Completed!") // sanity check
    $.ajax({
        url : "/resource/complete/", // the endpoint
        type : "POST", // http method
        data : { pk : $(clicked_resource).attr('value') }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $("#research-objectives").load(location.href+" #research-objectives>*","");
            console.log(json); // log the returned json to the console
            console.log("success"); // another sanity check
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};
