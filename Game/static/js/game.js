// $(function () {
//     update_attack_probabilities();
//     scrollChat();
//     //manager_sanction();
//     return false;
// });


// var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
// var chat_socket = new WebSocket(ws_scheme + '://' + window.location.host + "/webs" + window.location.pathname);

// Note that the path doesn't matter for routing; any WebSocket
// connection gets bumped over to WebSocket consumers
socket = new WebSocket("ws://" + window.location.host + "/chat/" + me_player.pk);
var clicked_research_resource;
var clicked_security_resource;


socket.onmessage = function (message) {
    var data = JSON.parse(message.data);
    console.log(data);

    if (data['type'] === 'resource_complete_response') {
        // Research resource complete action reply
        complete_research_resource_reply(data['response_message']);
    } else if (data['type'] === 'security_resource_activate_response') {
        // Security resource complete reply
        activate_security_resource_reply(data['response_message']);
    } else if (data['type'] === 'player_sanction_response') {
        // Player sanction reply
        sanction_player_reply(data['response_message']);
    } else if (data['type'] === 'pass_button_response') {
        // Pass button reply
        pass_round_reply(data['response_message']);
    } else if (data['type'] === 'player_update') {
        console.log("In player_update");
        update_player(data)
    } else if (data['type'] === 'update_message_board') {
        update_message_board(data);
    } else if (data['type'] === 'game_complete') {

    } else if (data['type'] === 'tick_complete') {
        update_ticks(data);
    } else if (data['type'] === 'sanction_status') {
        player_sanction(data);
    } else if (data['type'] === 'attack_type_update') {
        attack_inactivate_resource(data["attack_item"])
    } else if (data['type'] === 'move_made') {
        $("#game-number").text("Status:Waiting on others...");
    }

};


socket.onopen = function () {
    var message = {
        player_pk: me_player.toString(),
        type: "add_player"
    };
    socket.send(JSON.stringify(message));
};
// Call onopen directly if socket is already open
if (socket.readyState === WebSocket.OPEN) socket.onopen();

// $('#chatform').on('submit', function(event) {
//     var message = {
//         handle: $('#handle').val(),
//         message: $('#message').val(),
//     }
//     chat_socket.send(JSON.stringify(message));
//     return false;
// });
//
// chatsock.onmessage = function(message) {
//     var data = JSON.parse(message.data);
//     $('#chat').append('<tr>'
//         + '<td>' + data.timestamp + '</td>'
//         + '<td>' + data.handle + '</td>'
//         + '<td>' + data.message + ' </td>'
//     + '</tr>');
// };

function player_sanction(data) {
    if (data['sanctioned'] === 'True') {
        $("#passbtn").show();
    } else {
        $("#passbtn").hide();
    }

    // for (var index =0; index < data['sanction_threshold'].length;index++){
    //     if (data['sanction_threshold'][index] > 0){
    //            $("#vulnerability-list").find("#blue p:first").text(data['sanction_threshold'][index]);
    //     }else{
    //            $("#vulnerability-list").find("#blue p:first").text("");
    //     }
    // }
}

function attack_inactivate_resource(data) {
    for (var resource = 0; resource < data["immunity"].length; resource++) {
        if (data['immunity'][resource] == 'blue') {
            $("#vulnerability-list").find("#blue").removeClass("active").addClass("inactive").addClass("clickable");
        }
        if (data['immunity'][resource] == 'yellow') {
            $("#vulnerability-list").find("#yellow").removeClass("active").addClass("inactive").addClass("clickable");
        }
        if (data['immunity'][resource] == 'red') {
            $("#vulnerability-list").find("#red").removeClass("active").addClass("inactive").addClass("clickable");
        }
    }

    for (resource = 0; resource < data["capability"].length; resource++) {
        if (data['capability'][resource] == 'blue') {
            $("#capability-list").find("#blue").removeClass("active").addClass("inactive")
        }
        if (data['capability'][resource] == 'yellow') {
            $("#capability-list").find("#yellow").removeClass("active").addClass("inactive")
        }
        if (data['capability'][resource] == 'red') {
            $("#capability-list").find("#red").removeClass("active").addClass("inactive")
        }
    }

}


function update_player(player_object) {
    var tableObject = document.getElementById(player_object["id"]);
    if (tableObject != null) {
        console.log("Updating scores..");
        tableObject.rows[0].cells[0].textContent = "Score: " + player_object["score"];
        tableObject.rows[1].cells[1].textContent = player_object["status"];
        if (player_object["vulnerabilities"][0].active) {
            tableObject.rows[2].cells[1].children[0].className = "resource-container active"
        } else {
            tableObject.rows[2].cells[1].children[0].className = "resource-container inactive"
        }

        if (player_object["vulnerabilities"][1].active) {
            tableObject.rows[2].cells[2].children[0].className = "resource-container active"
        } else {
            tableObject.rows[2].cells[2].children[0].className = "resource-container inactive"
        }

        if (player_object["vulnerabilities"][2].active) {
            tableObject.rows[2].cells[3].children[0].className = "resource-container active"
        } else {
            tableObject.rows[2].cells[3].children[0].className = "resource-container inactive"
        }
    }
}

function update_ticks(tick_data) {
    // Update html of new rounds
    $("#game-number").text("Status: Your Move");

    if (tick_data["new_tick_count"] >= 0) {
        $("#time-remaining").text("Remaining Rounds: " + tick_data["new_tick_count"]);
    } else {
        $("#time-remaining").text("Game over!");
        console.log("Drawing the overlay");
        $('#game-over-modal').modal({backdrop: "static", keyboard: false});
    }

    if (tick_data["attack"] === 'red') {
        $("#attack_resource").addClass("red_attack");
    }

    if (tick_data["attack"] === 'blue') {
        $("#attack_resource").addClass("blue_attack");
    }

    if (tick_data["attack"] === 'yellow') {
        $("#attack_resource").addClass("yellow_attack");
    }

    if (tick_data["attack"] === 'lab') {
        $("#attack_resource").addClass("lab_attack");
    }
    if (tick_data["attack"] === '') {
        $("#attack_resource").removeClass("lab_attack").removeClass("yellow_attack").removeClass("red_attack").removeClass("blue_attack");
    }

}

function update_player_scores(player_score) {

}

function update_player_immunities() {

}

function update_player_progress() {

}

function update_message_board(data) {
    var message = data['message'];
    $("#talk").append('<li class="clearfix">' + message + '</li>');
    scrollChat();
}

function alertSuccess(message) {
    $(".response").empty();
    $(".response").append(
        '<div class="alert alert-success alert-dismissable">' +
        '<button type="button" class="close" ' +
        'data-dismiss="alert" aria-hidden="true">' +
        '&times;' +
        '</button>' +
        '<strong>Success:&nbsp;</strong>' +
        message +
        '</div>');
    return false;
}
function alertFailure(message) {
    $(".response").empty();
    $(".response").append(
        '<div class="alert alert-danger alert-dismissable">' +
        '<button type="button" class="close" ' +
        'data-dismiss="alert" aria-hidden="true">' +
        '&times;' +
        '</button>' +
        '<strong>Failure:&nbsp;</strong>' +
        message +
        '</div>');
    return false;
}
// Function for Attack Threat vertical bar
function update_attack_probabilities() {

    var animation_speed = 1000;

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
}

function game_complete() {
    $('#game-over-modal').modal({
        backdrop: "static",
        keyboard: false
    });
    clearinterval(roundUpdate);

}

// function tick_complete() {
//     window.location.reload();
// }

// Refreshes talk for new messages
function updateChat() {
    $("#talk").load(location.href + ' #talk');
    return false;
}
// Scrolls chat to bottom of screen when a message is send
function scrollChat() {
    var chatWindow = $(".panel-body.chat");
    $(chatWindow).animate({scrollTop: $(chatWindow)[0].scrollHeight}, 1000);
    return false;
}
// Updates Chat and the Left Panel
function updatePage() {
    $.ajax({
        url: location.href,
        success: function (json) {
            console.log("html request response");
            console.log(json);
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

// activate security resource
$(document).on('click', '.clickable.inactive', function (event) {
    event.preventDefault();
    clicked_security_resource = $(this);
    var message = {
        type: 'security_resource_activate',
        player_pk: $("#player").text(),
        security_resource_pk: $(this).attr('value')
    };
    socket.send(JSON.stringify(message));
    return false;
});


function activate_security_resource_reply(response_message) {
    if (response_message["active"] === true) {
        clicked_security_resource.removeClass("inactive").addClass("active");
        // $("#my-score").load(location.href +" #my-score>*","");
        // $("#my-vulnerabilities").load(location.href + " #my-vulnerabilities>*", "");
        $("#capability-list").load(location.href + " #capability-list>*", "");
        alertSuccess(response_message["result"]);
    } else {
        alertFailure(response_message["result"]);
    }
}

// complete research resource
$(document).on('click', '.clickable.incomplete', function (event) {
    alertSuccess("Response Recorded");
    var clicked_resource = $(this);
    clicked_research_resource = $(this);
    event.preventDefault();
    var message = {
        resource_pk: $(clicked_resource).attr('value'),
        player_pk: $("#player").text(),
        type: 'resource_complete'
    };
    socket.send(JSON.stringify(message));
    return false;
});


// sanction other player
$(document).on('click', '.sanction', function (event) {
    alertSuccess("Response Recorded");
    event.preventDefault();
    var message = {
        sanctionee_pk: $(this).attr("sanctionee"),
        sanctioner_pk: $(this).attr("sanctioner"),
        type: "player_sanction"
    };
    socket.send(JSON.stringify(message));
    return false;

});

function sanction_player_reply(response_message) {
    if ("sanctioned" in response_message && response_message["sanctioned"]) {
        // $("#my-score").load(location.href +" #my-score>*","");
        alertSuccess(response_message["result"]);
    } else {
        alertFailure(response_message["result"]);
    }
}

function complete_research_resource_reply(response_message) {
    if ("resource_complete" in response_message && response_message["resource_complete"] === true) {
        console.log("resource complete.");
        clicked_research_resource.removeClass("incomplete").addClass("complete");
        $("#my-score").text("Score: " + response_message['score']);
        alertSuccess(response_message["result"]);
    } else {
        alertFailure(response_message["result"]);
    }
    if ("objective_complete" in response_message && response_message["objective_complete"] === true) {
        $("#research-objectives").load(location.href + " #research-objectives>*", "");
    }
}


// when clicking on pass round button
$(document).on('click', '#passbtn', function (event) {
    alertSuccess("Response Recorded");
    var clicked_resource = $(this);
    event.preventDefault();
    var message = {
        player_pk: $("#player").text(),
        type: 'pass_button'

    };
    socket.send(JSON.stringify(message));
    return false;
});

function pass_round_reply(response_message) {
    if ("resource" in response_message) {
        if (response_message["resource"].includes("blue")) {

            $("#vulnerability-list").find("#blue").removeClass("inactive").addClass("active").removeClass("clickable");
            $("#capability-list").find("#blue").removeClass("inactive").addClass("active");
            $("#passbtn").hide();
            alertSuccess(response_message["result"]);
        }
        if (response_message["resource"].includes("red")) {
            $("#vulnerability-list").find("#red").removeClass("inactive").addClass("active").removeClass("clickable");
            $("#capability-list").find("#red").removeClass("inactive").addClass("active");
            $("#passbtn").hide();

            alertSuccess(response_message["result"]);
        }
        if (response_message["resource"].includes("yellow")) {
            $("#vulnerability-list").find("#yellow").removeClass("inactive").addClass("active").removeClass("clickable");
            $("#capability-list").find("#yellow").removeClass("inactive").addClass("active");
            $("#passbtn").hide();
            alertSuccess(response_message["result"]);
        }
        if (response_message["resource"] === "null") {
            alertSuccess(response_message["result"]);
        }
    } else {
        alertFailure(response_message["result"]);
    }
}

