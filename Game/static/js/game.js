// $(function () {
//     update_attack_probabilities();
//     scrollChat();
//     //manager_sanction();
//     return false;
// });

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

function player_sanction(data) {

    for (var indexOut = 0; indexOut < data['sanction_dict'].length; indexOut++) {

        if (data['sanction_dict'][indexOut]['player_id'] === me_player) {
            if (data['sanction_dict'][indexOut]['sanctioned'] === 'True') {
                show_pass_button();
            } else {
                hide_pass_button();
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

function handle_capability(data) {
    if (data["blue_capability"]) {
        activate_blue_capability();
    } else {
        deactivate_blue_capability();
    }

    if (data["red_capability"]) {
        activate_red_capability();
    } else {
        deactivate_red_capability();
    }

    if (data["yellow_capability"]) {
        activate_yellow_capability();
    } else {
        deactivate_yellow_capability();
    }

}

function handle_security(data) {

    if (data["blue_security"]["active"]) {
        activate_blue_security();
    } else {
        deactivate_blue_security(data["blue_security"]["deadline_sanction"]);
    }

    if (data["red_security"]["active"]) {
        activate_red_security();
    } else {
        deactivate_red_security(data["red_security"]["deadline_sanction"]);
    }

    if (data["yellow_security"]["active"]) {
        activate_yellow_security();
    } else {
        deactivate_yellow_security(data["yellow_security"]["deadline_sanction"]);
    }

}

function activate_red_security() {
    var securityObjectUpdate = document.getElementById("red_security");
    securityObjectUpdate.classList.remove("inactive");
    securityObjectUpdate.classList.remove("clickable");
    securityObjectUpdate.classList.add("active");
    securityObjectUpdate.textContent = "";
}

function deactivate_red_security(deadline) {
    var securityObjectUpdate = document.getElementById("red_security");
    securityObjectUpdate.classList.add("inactive");
    securityObjectUpdate.classList.remove("active");
    securityObjectUpdate.classList.add("clickable");
    securityObjectUpdate.textContent = deadline;
}

function activate_red_capability() {
    var securityObjectUpdate = document.getElementById("red_capability");
    securityObjectUpdate.classList.remove("inactive");
    securityObjectUpdate.classList.add("active");
}

function deactivate_red_capability() {
    var securityObjectUpdate = document.getElementById("red_capability");
    securityObjectUpdate.classList.add("inactive");
    securityObjectUpdate.classList.remove("active");
}

function activate_yellow_capability() {
    var securityObjectUpdate = document.getElementById("yellow_capability");
    securityObjectUpdate.classList.remove("inactive");
    securityObjectUpdate.classList.add("active");
}

function activate_yellow_security() {
    var securityObjectUpdate = document.getElementById("yellow_security");
    securityObjectUpdate.classList.remove("inactive");
    securityObjectUpdate.classList.remove("clickable");
    securityObjectUpdate.classList.add("active");
    securityObjectUpdate.textContent = "";
}

function deactivate_yellow_capability() {
    var securityObjectUpdate = document.getElementById("yellow_capability");
    securityObjectUpdate.classList.add("inactive");
    securityObjectUpdate.classList.remove("active");
}

function deactivate_yellow_security(deadline) {
    var securityObjectUpdate = document.getElementById("yellow_security");
    securityObjectUpdate.classList.add("inactive");
    securityObjectUpdate.classList.remove("active");
    securityObjectUpdate.classList.add("clickable");
    securityObjectUpdate.textContent = deadline;
}

function activate_blue_capability() {
    var securityObjectUpdate = document.getElementById("blue_capability");
    securityObjectUpdate.classList.remove("inactive");
    securityObjectUpdate.classList.add("active");
}


function activate_blue_security() {
    var securityObjectUpdate = document.getElementById("blue_security");
    securityObjectUpdate.classList.remove("inactive");
    securityObjectUpdate.classList.remove("clickable");
    securityObjectUpdate.classList.add("active");
    securityObjectUpdate.textContent = "";
}

function deactivate_blue_capability() {
    var securityObjectUpdate = document.getElementById("blue_capability");
    securityObjectUpdate.classList.add("inactive");
    securityObjectUpdate.classList.remove("active");
}


function deactivate_blue_security(deadline) {
    var securityObjectUpdate = document.getElementById("blue_security");
    securityObjectUpdate.classList.add("inactive");
    securityObjectUpdate.classList.remove("active");
    securityObjectUpdate.classList.add("clickable");
    securityObjectUpdate.textContent = deadline;
}

function update_player(player_object) {
    var tableObject = document.getElementById(player_object["id"]);
    if (tableObject !== null) {
        tableObject.rows[0].cells[1].textContent = "$" + player_object["score"];
        tableObject.rows[1].cells[1].textContent = player_object["status"];
        handle_security(player_object);
        handle_capability(player_object);
    }
}

function update_attack(attack_type) {

    $("#attack_resource").removeClass("lab_attack").removeClass("yellow_attack").removeClass("red_attack").removeClass("blue_attack");

    if (attack_type === 'red') {
        $("#attack_resource").addClass("red_attack");
    }

    if (attack_type === 'blue') {
        $("#attack_resource").addClass("blue_attack");
    }

    if (attack_type === 'yellow') {
        $("#attack_resource").addClass("yellow_attack");
    }

    if (attack_type === 'lab') {
        $("#attack_resource").addClass("lab_attack");
    }

}

function show_pass_button() {
    $("#passbtn").show();
}

function hide_pass_button() {
    $("#passbtn").hide();
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

    if (tick_data['sanctioned']){
        show_pass_button();
    }else{
        hide_pass_button();
    }
    update_attack(tick_data["attack"]);
    handle_security(tick_data);
    handle_capability(tick_data);


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
    alertSuccess("Response Recorded");
    event.preventDefault();
    var message = {
        type: 'security_resource_activate',
        player_pk: $("#player").text(),
        security_resource_pk: $(this).attr('id')
    };
    socket.send(JSON.stringify(message));
    return false;
});

// complete research resource
$('#projects').on('click', '.clickable.incomplete', function (event) {
    alertSuccess("Response Recorded");
    event.preventDefault();
    var id = this.id;
    var resource_type = id.split("_")[0];
    var resource_position = id.split("_")[1];
    var message = {
        resource_type: resource_type,
        resource_position: resource_position,
        player_pk: $("#player").text(),
        type: 'resource_complete'
    };
    console.log("Resource Clicked");
    console.log(message);
    socket.send(JSON.stringify(message));
    return false;
});


function activate_security_resource_reply(response_message) {

    if (response_message["active"] === true) {
        handle_security(response_message);
        handle_capability(response_message);
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

function change_resource_classification(resource_object, new_classification) {
    resource_object.className = '';
    resource_object.classList.add("clickable");
    resource_object.classList.add("resource-container");
    resource_object.classList.add("incomplete");
    resource_object.classList.add(new_classification)

}

function complete_research_resource_reply(response_message) {
    if (response_message['objective_complete'] === true) {
        if (response_message['resource_type'] === 'workshop') {
            var querySelectorquery = document.getElementById('workshop_resource');
            change_resource_classification(querySelectorquery, response_message['new_classifications'][0]);
        } else if (response_message['resource_type'] === 'conference') {
            var querySelectorquery = document.getElementById('conference_one');
            change_resource_classification(querySelectorquery, response_message['new_classifications'][0]);
            querySelectorquery = document.getElementById('conference_two');
            change_resource_classification(querySelectorquery, response_message['new_classifications'][1]);

        } else {
            var querySelectorquery = document.getElementById('journal_one');
            change_resource_classification(querySelectorquery, response_message['new_classifications'][0]);
            querySelectorquery = document.getElementById('journal_two');
            change_resource_classification(querySelectorquery, response_message['new_classifications'][1]);
            querySelectorquery = document.getElementById('journal_three');
            change_resource_classification(querySelectorquery, response_message['new_classifications'][2]);

        }
        $("#my-score").text("$" + response_message['score']);
        alertSuccess(response_message["result"]);
    } else if ("resource_complete" in response_message && response_message["resource_complete"] === true) {
        var idName = response_message['resource_type'] + '_' + response_message['resource_position'];
        var querySelectorquery = document.getElementById(idName);
        querySelectorquery.classList.remove("incomplete");
        querySelectorquery.classList.add("complete");

        $("#my-score").text("$" + response_message['score']);
        alertSuccess(response_message["result"]);
    } else {
        alertFailure(response_message["result"]);
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
            activate_blue_security();
            activate_blue_capability();
            hide_pass_button();
            alertSuccess(response_message["result"]);
        }
        if (response_message["resource"].includes("red")) {
            activate_red_security();
            activate_red_capability();
            hide_pass_button();

            alertSuccess(response_message["result"]);
        }
        if (response_message["resource"].includes("yellow")) {
            activate_yellow_security();
            activate_blue_capability();
            hide_pass_button();
            alertSuccess(response_message["result"]);
        }
        if (response_message["resource"] === "null") {
            alertSuccess(response_message["result"]);
        }
    } else {
        alertFailure(response_message["result"]);
    }
}

