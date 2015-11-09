
$(function() {
    update_attack_probabilities();
    scrollChat();
});

// Function for Attack Threat vertical bar
function update_attack_probabilities(){

    var animation_speed = 0

    // Get blue threat
    var blueBar = $('.attack-threat').find('.inner.blue');
    var blueThreat = blueBar.attr("blue-threat");

    // Animate bar
    $(blueBar).animate({
        height: blueThreat
    }, animation_speed);

     // Get blue threat
    var redBar = $('.attack-threat').find('.inner.red');
    var redThreat = parseInt(redBar.attr("red-threat")) + parseInt(blueThreat);
    var redCent = redThreat + "%";

    // Animate bar
    $(redBar).animate({
        height: redCent
    }, animation_speed);

    // Get blue threat
    var yellowBar = $('.attack-threat').find('.inner.yellow');
    var yellowThreat = parseInt(yellowBar.attr("yellow-threat")) + redThreat;
    var yellowCent = yellowThreat + "%";

    // Animate bar
    $(yellowBar).animate({
        height: yellowCent
    }, animation_speed);

};


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
        data : { the_message : $('#id_content').val(), game_key : $('#game-key').text()}, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $('#id_content').val(''); // remove the value from the input
            updatePage();
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

// Keeps chat and other players' scores and vulnerabilities up-to-date
function updatePage(){
    $("#talk").load(location.href +  ' #talk');
    $("#left-panel").load(location.href +" #left-panel>*","");
    $("#attack").load(location.href +" #attack>*","");
    $("#vulnerability-list").load(location.href +" #vulnerability-list>*","");
    $("#vulnerabilities").load(location.href +" #vulnerabilities>*","");
    $("#time-remaining").load(location.href +" #time-remaining");
    scrollChat();
}

setInterval("updatePage()", 800);  //call updatePage() function every 1 seconds


// AJAX POST activate security resource
$(document).on('click', '.clickable.inactive',function(event){
    var clicked_resource = $(this);
    event.preventDefault();
    console.log("resource clicked");  // sanity check
    activate_security_resource(clicked_resource);
});

function activate_security_resource(clicked_resource) {
    console.log("Security Resource Activated!") // sanity check
    $.ajax({
        url : "/resource/activate/", // the endpoint
        type : "POST", // http method
        data : { pk : $(clicked_resource).attr('value'), player_pk : $("#player").text() }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $(clicked_resource).removeClass("inactive").addClass("active")
            $("#vulnerability-list").load(location.href +" #vulnerability-list>*","");
            $("#vulnerabilities").load(location.href +" #vulnerabilities>*","");
            $("#time-remaining").load(location.href +" #time-remaining");
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
    event.preventDefault();
    console.log("resource clicked");  // sanity check
    complete_research_resource(clicked_resource);
});

function complete_research_resource(clicked_resource) {
    console.log("Research Resource Completed!") // sanity check
    $.ajax({
        url : "/resource/complete/", // the endpoint
        type : "POST", // http method
        data : { pk : $(clicked_resource).attr('value'), player_pk : $("#player").text() }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $(clicked_resource).removeClass("incomplete").addClass("complete")
            $("#research-objectives").load(location.href+" #research-objectives>*","");
            $("#time-remaining").load(location.href +" #time-remaining");
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

// AJAX POST impose sanction on player
// $(document).on('click', '.clickable.incomplete', function(event){
//     var clicked_resource = $(this);
//     // Change class from .incomplete to .complete
//     clicked_resource.removeClass("incomplete").addClass("complete");
//     event.preventDefault();
//     console.log("resource clicked");  // sanity check
//     var color = clicked_resource.attr('id');
//     complete_research_resource(clicked_resource);
// });

// function complete_research_resource(clicked_resource) {
//     console.log("Research Resource Completed!") // sanity check
//     $.ajax({
//         url : "/sanction/", // the endpoint
//         type : "POST", // http method
//         data : { pk : $(clicked_resource).attr('value') }, // data sent with the post request

//         // handle a successful response
//         success : function(json) {
//             $("#research-objectives").load(location.href+" #research-objectives>*","");
//             console.log(json); // log the returned json to the console
//             console.log("success"); // another sanity check
//         },

//         // handle a non-successful response
//         error : function(xhr,errmsg,err) {
//             $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
//                 " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
//             console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
//         }
//     });
// };
