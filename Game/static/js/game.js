$(function() {
    update_attack_probabilities();
    scrollChat();
    //manager_sanction();
    return false;
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
    return false;
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
    return false;
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

    return false;
};


// AJAX POST message for game chat
$('#message-form').on('submit', function(event){
    event.preventDefault();
    create_message();
    return false;
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
    return false;
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
                $('#game-over-modal').modal({
                    backdrop : "static",
                    keyboard : false,
                    });
                clearinterval(roundUpdate);
            } else if (json["tick_complete"] === true) {
                //if a tick is complete, do manager sanction in check_tick_complete in views.py           
                window.location.reload();
            } else {
                updatePage();
            }
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
    return false;
};

var roundUpdate = setInterval(function() {updateRound() }, 3000);  //call updateRound() function every 3 seconds

// Refreshes talk for new messages
function updateChat() {
    $("#talk").load(location.href +  ' #talk');
    return false;
};

// Scrolls chat to bottom of screen when a message is send
function scrollChat() {
    var chatWindow = $(".panel-body.chat");
    $(chatWindow).animate({scrollTop:$(chatWindow)[0].scrollHeight}, 1000);
    return false;
};

// Updates Chat and the Left Panel
function updatePage() {
    $.ajax({
        url: location.href,
        success: function(json) {

            // Update left panel
            var gameInfo = $(json).find("#game-info").html();
            $('#game-info').html(gameInfo);

            // Update Chat
            var old_talk = $("#talk").html();
            var new_talk = $(json).find("#talk").html();
            if (old_talk !== new_talk) {
                $('#talk').html(new_talk);
                scrollChat();
            }
        }
    });
    return false;
}

// AJAX POST activate security resource
$(document).on('click', '.clickable.inactive',function(event){
    var clicked_resource = $(this);
    event.preventDefault();
    activate_security_resource(clicked_resource);
    return false;
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
                $("#my-vulnerabilities").load(location.href +" #my-vulnerabilities>*","");
                $("#capability-list").load(location.href +" #capability-list>*","");
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
    return false;
};

// AJAX POST complete research resource
$(document).on('click', '.clickable.incomplete', function(event){
    var clicked_resource = $(this);
    event.preventDefault();
    complete_research_resource(clicked_resource);
    return false;
});


// AJAX POST sanction other player
$(document).on('click', '.sanction', function(event){
    var sanctionee_pk = $(this).attr("sanctionee");
    var sanctioner_pk = $(this).attr("sanctioner");
    var tick_pk = $("#time-remaining").attr("value");
    event.preventDefault();
    sanction_other_player(sanctionee_pk, sanctioner_pk, tick_pk);
    return false;

});

function sanction_other_player(sanctionee_pk, sanctioner_pk, tick_pk) {
    $.ajax({
        url : "/player/sanction/", // the endpoint
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
    return false;

};


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
    return false;
};

// AJAX POST impose sanction on player
$(document).on("click", ".sanction_abc", function(event){
    var sanctionee_pk = $(this).attr("sanctionee");
    var sanctioner_pk = $(this).attr("sanctioner");
    var tick_pk = $("#time-remaining").attr("value");
    event.preventDefault();
    sanction_player(sanctionee_pk, sanctioner_pk, tick_pk);
    return false;
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
    return false;
};


// AJAX POST when clicking on pass round button
$(document).on('click', '#passbtn', function(event){
    var clicked_resource = $(this);
    event.preventDefault();
    pass_round(clicked_resource);
    return false;
});

//skip one round
function pass_round(clicked_resource) {
    $.ajax({
        url : "/passround/", // the endpoint
        type : "POST", // http method
        data : {player_pk : $("#player").text() }, // data sent with the post request

        // handle a successful response
        success : function(json) {
            if (json["resource"] == "blue") {
                $('#blue').removeClass("inactive").addClass("active");
                $("#my-vulnerabilities").load(location.href +" #my-vulnerabilities>*","");
                $("#capability-list").load(location.href +" #capability-list>*","");
                alertSuccess(json["result"]);
            } else if (json["resource"] == "red") {
                $('#red').removeClass("inactive").addClass("active");
                $("#my-vulnerabilities").load(location.href +" #my-vulnerabilities>*","");
                $("#capability-list").load(location.href +" #capability-list>*","");
                alertSuccess(json["result"]);
            } else if (json["resource"] == "yellow") {
                $('#yellow').removeClass("inactive").addClass("active");
                $("#my-vulnerabilities").load(location.href +" #my-vulnerabilities>*","");
                $("#capability-list").load(location.href +" #capability-list>*","");
                alertSuccess(json["result"]);
            } else if (json["resource"] == "null") {
                alertSuccess(json["result"]);
            } else{
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
    return false;
};