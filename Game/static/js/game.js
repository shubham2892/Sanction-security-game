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

socket.onmessage = function (message) {
    var data = JSON.parse(message.data);

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

    for (var indexOut = 0; indexOut < data['sanction_dict'].length; indexOut++) {

        if (data['sanction_dict'][indexOut]['player_id'] === me_player) {
            if (data['sanction_dict'][indexOut]['sanctioned'] === 'True') {
                $("#passbtn").show();
            } else {
                $("#passbtn").hide();
            }

            for (var index = 0; index < data['sanction_dict'][indexOut]['sanction_threshold'].length; index++) {
                var querySelectorquery = 'div[value="' + data['sanction_dict'][indexOut]['immunity_ids'][index] + '"]';
                if (data['sanction_dict'][indexOut]['immunity_status'][index] !== -1) {
                    if (data['sanction_dict'][indexOut]['sanction_threshold'][index] > 0) {
                        document.querySelector(querySelectorquery).textContent = data['sanction_dict'][indexOut]['sanction_threshold'][index];
                    } else {
                        document.querySelector(querySelectorquery).textContent = 'X';
                    }

                } else {
                    document.querySelector(querySelectorquery).textContent = "";
                }
            }
        }
    }
}

function attack_inactivate_resource(data) {
    for (var resource = 0; resource < data["immunity"].length; resource++) {
        if (data['immunity'][resource] === 'blue') {

            $("#vulnerability-list").find("#blue").removeClass("active").addClass("inactive").addClass("clickable");
        }
        if (data['immunity'][resource] === 'yellow') {
            $("#vulnerability-list").find("#yellow").removeClass("active").addClass("inactive").addClass("clickable");
        }
        if (data['immunity'][resource] === 'red') {
            $("#vulnerability-list").find("#red").removeClass("active").addClass("inactive").addClass("clickable");
        }
    }

    for (resource = 0; resource < data["capability"].length; resource++) {
        if (data['capability'][resource] === 'blue') {
            $("#capability-list").find("#blue").removeClass("active").addClass("inactive")
        }
        if (data['capability'][resource] === 'yellow') {
            $("#capability-list").find("#yellow").removeClass("active").addClass("inactive")
        }
        if (data['capability'][resource] === 'red') {
            $("#capability-list").find("#red").removeClass("active").addClass("inactive")
        }
    }

}


function update_player(player_object) {
    var tableObject = document.getElementById(player_object["id"]);
    if (tableObject !== null) {
        tableObject.rows[0].cells[1].textContent = "$" + player_object["score"];
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
function game_complete() {
    $('#game-over-modal').modal({
        backdrop: "static",
        keyboard: false
    });
    clearinterval(roundUpdate);

}

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
$('#security_objectives').on('click', '.clickable.inactive', function (event) {
    console.log("Security Resource clicked: " + $(this).attr('value'));
    alertSuccess("Response Recorded");
    event.preventDefault();
    var message = {
        type: 'security_resource_activate',
        player_pk: $("#player").text(),
        security_resource_pk: $(this).attr('value')
    };
    socket.send(JSON.stringify(message));
    return false;
});

// complete research resource
$('#projects').on('click', '.clickable.incomplete', function (event) {
    alertSuccess("Response Recorded");
    var clicked_resource = $(this);
    event.preventDefault();
    var message = {
        resource_pk: $(clicked_resource).attr('value'),
        player_pk: $("#player").text(),
        type: 'resource_complete'
    };
    socket.send(JSON.stringify(message));
    return false;
});


function activate_security_resource_reply(response_message) {
    if (response_message["active"] === true) {
        var querySelectorquery = 'div[value="' + response_message['pk'] + '"]';
        document.querySelector(querySelectorquery).textContent = "";
        document.querySelector(querySelectorquery).classList.remove("inactive");
        document.querySelector(querySelectorquery).classList.add("active");
        $("#capability-list").load(location.href + " #capability-list>*", "");
        alertSuccess(response_message["result"]);
    } else {
        alertFailure(response_message["result"]);
    }
}


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
        alertSuccess(response_message["result"]);
    } else {
        alertFailure(response_message["result"]);
    }
}

function complete_research_resource_reply(response_message) {
    if ("resource_complete" in response_message && response_message["resource_complete"] === true) {
        var querySelectorquery = 'div[value="' + response_message['clicked_resource'] + '"]';
        document.querySelector(querySelectorquery).classList.remove("incomplete");
        document.querySelector(querySelectorquery).classList.add("complete");

        $("#my-score").text("$" + response_message['score']);
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
            $("#vulnerability-list").find("#blue").text("");
            $("#capability-list").find("#blue").removeClass("inactive").addClass("active");
            $("#passbtn").hide();
            alertSuccess(response_message["result"]);
        }
        if (response_message["resource"].includes("red")) {
            $("#vulnerability-list").find("#red").removeClass("inactive").addClass("active").removeClass("clickable");
            $("#vulnerability-list").find("#red").text("");
            $("#capability-list").find("#red").removeClass("inactive").addClass("active");
            $("#passbtn").hide();

            alertSuccess(response_message["result"]);
        }
        if (response_message["resource"].includes("yellow")) {
            $("#vulnerability-list").find("#yellow").removeClass("inactive").addClass("active").removeClass("clickable");
            $("#vulnerability-list").find("#yellow").text("");
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

