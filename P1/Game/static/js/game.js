
$(function() {
    update_attack_probabilities();
    scrollChat();
});

function alertSuccess(message) {
    $(".response").empty();
    $(".response").append(
        '<div class="alert alert-success alert-dismissable">'+
            '<button type="button" class="close" ' +
                    'data-dismiss="alert" aria-hidden="true">' +
                '&times;' +
            '</button>' +
            '<strong>Success:&nbsp;</strong>' +
            message +
         '</div>');
};

function alertFailure(message) {
    $(".response").empty();
    $(".response").append(
        '<div class="alert alert-danger alert-dismissable">'+
            '<button type="button" class="close" ' +
                    'data-dismiss="alert" aria-hidden="true">' +
                '&times;' +
            '</button>' +
            '<strong>Failure:&nbsp;</strong>' +
            message +
         '</div>');
};


// Function for Attack Threat vertical bar
function update_attack_probabilities(){

    var animation_speed = 1000

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
    create_message();
});

function create_message() {
    $.ajax({
        url : "/message/create/", // the endpoint
        type : "POST", // http method
        data : { the_message : $('#id_content').val(), game_key : $('#game-key').text()}, // data sent with the post request

        // handle a successful response
        success : function(json) {
            $('#id_content').val(''); // remove the value from the input
            updateChat();
            scrollChat();
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};


// Updates round after all players have moved
function updateRound() {
    $.ajax({
        url : "/tick/complete/", // the endpoint
        type : "POST", // http method
        data : { tick_pk : $("#time-remaining").attr('value')}, // data sent with the post request

        // handle a successful response
        success : function(json) {
            if (json["game_complete"] === true) {
                clearInterval(roundUpdate);
                clearInterval(pageUpdate);
                $('#game-over-modal').modal({
                    backdrop : "static",
                    keyboard : false,
                    });
            } else if (json["tick_complete"] === true) {
                window.location.reload();
            }
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};

var roundUpdate = setInterval(function() {updateRound() }, 3000);  //call updateRound() function every 2 seconds

// Updates for new messages and keeps chat scrolled to the bottom
function updateChat() {
    $("#talk").load(location.href +  ' #talk');
};

function scrollChat() {
    var chatWindow = $(".panel-body.chat");
    $(chatWindow).animate({scrollTop:$(chatWindow)[0].scrollHeight}, 1000);
};

function updateLeftPanel() {
    $("#their-score").load(location.href + " #their-score");
    $("#their-vulnerabilities").load(location.href + " #their-vulnerabilities");
}

// Keeps chat and other players' scores and vulnerabilities up-to-date
function updatePage(){
    updateLeftPanel();
    updateChat();
}

var pageUpdate = setInterval(function() {updatePage() }, 3000);  //call updatePage() function every 1 seconds


// AJAX POST activate security resource
$(document).on('click', '.clickable.inactive',function(event){
    var clicked_resource = $(this);
    event.preventDefault();
    activate_security_resource(clicked_resource);
});

function activate_security_resource(clicked_resource) {
    $.ajax({
        url : "/resource/activate/", // the endpoint
        type : "POST", // http method
        data : { pk : $(clicked_resource).attr('value'), player_pk : $("#player").text() }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            if (json["active"] === true) {
                $(clicked_resource).removeClass("inactive").addClass("active")
                $("#my-score").load(location.href +" #my-score>*","");
                $("#capability-list").load(location.href +" #capability-list>*","");
                $("#my-vulnerabilities").load(location.href +" #my-vulnerabilities>*","");
                alertSuccess(json["result"]);
            } else {
                alertFailure(json["result"]);
            }

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
    complete_research_resource(clicked_resource);
});

function complete_research_resource(clicked_resource) {
    $.ajax({
        url : "/resource/complete/", // the endpoint
        type : "POST", // http method
        data : { pk : $(clicked_resource).attr('value'), player_pk : $("#player").text() }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            if (json["resource_complete"] === true) {
                $(clicked_resource).removeClass("incomplete").addClass("complete");
                $("#my-score").load(location.href +" #my-score>*","");
                alertSuccess(json["result"]);
            } else {
                alertFailure(json["result"]);
            }
            if (json["objective_complete"] === true) {
                $("#research-objectives").load(location.href +" #research-objectives>*","");
            }

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
$("#sanction").click(function(event){
    var sanctionee_pk = $(this).attr("sanctionee");
    var sanctioner_pk = $(this).attr("sanctioner");
    var tick_pk = $("#time-remaining").attr("value");
    event.preventDefault();
    sanction_player(sanctionee_pk, sanctioner_pk, tick_pk);
});

function sanction_player(sanctionee_pk, sanctioner_pk, tick_pk) {
    $.ajax({
        url : "/sanction/", // the endpoint
        type : "POST", // http method
        data : { sanctionee_pk : sanctionee_pk, sanctioner_pk: sanctioner_pk, tick_pk : tick_pk }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            if (json["sanctioned"]) {
                $("#my-score").load(location.href +" #my-score>*","");
                alertSuccess(json["result"]);
            } else {
                alertFailure(json["result"]);
            }
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
};
