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
socket = new WebSocket("ws://" + window.location.host + "/chat/");
var clicked_research_resource;
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

    } else if (data['type'] === 'game_complete') {

    } else if (data['type'] === 'tick_complete') {
        update_ticks(data["new_tick_count"]);
    }
};
socket.onopen = function () {

};
// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();

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

function update_ticks(new_tick_count) {
    // Update html of new rounds
    if (new_tick_count > 0) {
        $(".time-remaining").textContent = new_tick_count;
    } else {
        $(".time-remaining").textContent = "Game over!";
    }
}

function update_player_scores(player_score) {

}

function update_player_immunities() {

}

function update_player_progress() {

}

function update_message_board() {

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
};

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
};

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

function tick_complete() {
    window.location.reload();
}

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
    var message = {
        type: 'security_resource_activate',
        player_pk: $("#player").text(),
        security_resource_pk: $(this).attr('value')
    };
    socket.send(JSON.stringify(message));
    return false;
});


function activate_security_resource_reply(response_message) {
    if (response_message["active"] == true) {
        $(clicked_resource).removeClass("inactive").addClass("active");
        // $("#my-score").load(location.href +" #my-score>*","");
        $("#my-vulnerabilities").load(location.href + " #my-vulnerabilities>*", "");
        $("#capability-list").load(location.href + " #capability-list>*", "");
        alertSuccess(response_message["result"]);
    } else {
        alertFailure(response_message["result"]);
    }
}

// complete research resource
$(document).on('click', '.clickable.incomplete', function (event) {
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
    event.preventDefault();
    var message = {
        sanctionee_pk: $(this).attr("sanctionee"),
        sanctioner_pk: $(this).attr("sanctioner"),
        tick_pk: $("#time-remaining").attr("value"),
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
        $("#my-score").load(location.href +" #my-score>*","");
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
    if (response_message["resource"] == "blue") {
        $('#blue').removeClass("inactive").addClass("active");
        $("#my-vulnerabilities").load(location.href + " #my-vulnerabilities>*", "");
        $("#capability-list").load(location.href + " #capability-list>*", "");
        alertSuccess(response_message["result"]);
    } else if (response_message["resource"] == "red") {
        $('#red').removeClass("inactive").addClass("active");
        $("#my-vulnerabilities").load(location.href + " #my-vulnerabilities>*", "");
        $("#capability-list").load(location.href + " #capability-list>*", "");
        alertSuccess(response_message["result"]);
    } else if (response_message["resource"] == "yellow") {
        $('#yellow').removeClass("inactive").addClass("active");
        $("#my-vulnerabilities").load(location.href + " #my-vulnerabilities>*", "");
        $("#capability-list").load(location.href + " #capability-list>*", "");
        alertSuccess(response_message["result"]);
    } else if (response_message["resource"] == "null") {
        alertSuccess(response_message["result"]);
    } else {
        alertFailure(response_message["result"]);
    }
}

