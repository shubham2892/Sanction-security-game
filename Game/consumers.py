import json
import random

from channels import Group
from django.contrib.humanize.templatetags.humanize import apnumber

from Game.models import Player, PlayerTick, Sanction, SANCTION, PASS, Message, RED, YELLOW, \
    Workshop, Conference, Journal, RESOURCE_CLASSIFICATIONS, \
    SECURITY_BLUE, SECURITY_RED, SECURITY_YELLOW, RESEARCH_TASK


def check_player_capability(workshop_classification, player):
    if workshop_classification == RED:
        if not player.red_status_capability:
            return False
    elif workshop_classification == YELLOW:
        if not player.yellow_status_capability:
            return False
    else:
        if not player.blue_status_capability:
            return False
    return True


def resource_complete(player_pk, resource_type, resource_position, message):
    player = Player.objects.select_related('game').get(id=player_pk)
    player_tick = PlayerTick(player=player, tick_number=player.game.ticks)
    response_message = {}
    if player.can_move:
        if player.manager_sanctioned:
            response_message[
                "result"] = "You have been sanctioned by the manager. You can only click on the 'Pass' button to pass this round."
            response_complete_json = {"type": "resource_complete_response",
                                      "response_message": response_message}
            message.reply_channel.send({"text": json.dumps(response_complete_json)})

        elif player.sanctioned:
            response_message[
                "result"] = "You have been peer sanctioned. You can only click on the 'Pass' button to pass this round."
            response_complete_json = {"type": "resource_complete_response",
                                      "response_message": response_message}
            message.reply_channel.send({"text": json.dumps(response_complete_json)})
        else:
            objective_completed = False
            new_classifications = []
            NOT_CAPABLE_ERROR_MESSAGE = "You are not capable of completing this task. Make sure you patch your capabilities."
            if resource_type == "workshop":
                workshop = Workshop.objects.get(player=player_pk)
                resource_classification = workshop.classification
                if not check_player_capability(resource_classification, player):
                    response_message['result'] = NOT_CAPABLE_ERROR_MESSAGE
                    response_complete_json = {"type": "resource_complete_response",
                                              "response_message": response_message}
                    message.reply_channel.send({"text": json.dumps(response_complete_json)})

                    return

                player.nf_workshop += 1
                player.score += workshop.score

                if workshop.classification == RED:
                    player.nf_red += 1
                elif workshop.classification == YELLOW:
                    player.nf_yellow += 1
                else:
                    player.nf_red += 1

                random_number = random.randint(1, 3)
                workshop.classification = random_number
                workshop.count = workshop.count + 1
                workshop.save()
                objective_completed = True
                new_classifications.append(workshop.classification_display)


            elif resource_type == 'conference':
                conference = Conference.objects.get(player=player_pk)

                if resource_position == 'one':
                    resource_classification = conference.classification_one
                else:
                    resource_classification = conference.classification_two

                if not check_player_capability(resource_classification, player):
                    response_message['result'] = NOT_CAPABLE_ERROR_MESSAGE
                    response_complete_json = {"type": "resource_complete_response",
                                              "response_message": response_message}
                    message.reply_channel.send({"text": json.dumps(response_complete_json)})

                    return

                if resource_position == 'one':
                    conference.complete_one = True
                else:
                    conference.complete_two = True

                if resource_classification == RED:
                    player.nf_red += 1
                elif resource_classification == YELLOW:
                    player.nf_yellow += 1
                else:
                    player.nf_red += 1

                if conference.complete_one and conference.complete_two:
                    conference.complete_two = False
                    conference.complete_one = False
                    conference.classification_one = random.randint(1, 3)
                    conference.classification_two = random.randint(1, 3)
                    new_classifications.append(conference.classification_display_one)
                    new_classifications.append(conference.classification_display_two)
                    conference.count = conference.count + 1
                    player.score += conference.score
                    objective_completed = True
                    player.nf_conference += 1
                else:
                    objective_completed = False

                conference.save()

            else:
                journal = Journal.objects.get(player=player_pk)

                if resource_position == 'one':
                    resource_classification = journal.classification_one
                elif resource_position == 'two':
                    resource_classification = journal.classification_two
                else:
                    resource_classification = journal.classification_three

                if not check_player_capability(resource_classification, player):
                    response_message['result'] = NOT_CAPABLE_ERROR_MESSAGE
                    response_complete_json = {"type": "resource_complete_response",
                                              "response_message": response_message}
                    message.reply_channel.send({"text": json.dumps(response_complete_json)})

                    return

                if resource_position == 'one':
                    journal.complete_one = True
                elif resource_position == 'two':
                    journal.complete_two = True
                else:
                    journal.complete_three = True

                if resource_classification == RED:
                    player.nf_red += 1
                elif resource_classification == YELLOW:
                    player.nf_yellow += 1
                else:
                    player.nf_red += 1

                if journal.complete_one and journal.complete_two and journal.complete_three:
                    journal.classification_one = random.randint(1, 3)
                    journal.classification_two = random.randint(1, 3)
                    journal.classification_three = random.randint(1, 3)
                    journal.complete_one = False
                    journal.complete_two = False
                    journal.complete_three = False
                    player.score += journal.score
                    objective_completed = True
                    player.nf_journal += 1
                    new_classifications.append(journal.classification_display_one)
                    new_classifications.append(journal.classification_display_two)
                    new_classifications.append(journal.classification_display_three)

                journal.save()

            if objective_completed:
                response_message['result'] = resource_type.title() + " Completed!"
            else:
                response_message['result'] = RESOURCE_CLASSIFICATIONS[resource_classification - 1][
                                                 1].title() + " Completed!"

            # End players move
            player.save()

            response_message['resource_complete'] = True
            response_message['objective_complete'] = objective_completed
            response_message['new_classifications'] = new_classifications
            response_message['resource_type'] = resource_type
            response_message['resource_position'] = resource_position
            response_message['score'] = player.score

            response_complete_json = {"type": "resource_complete_response",
                                      "response_message": response_message}
            message.reply_channel.send({"text": json.dumps(response_complete_json)})

            player_tick.action = RESEARCH_TASK
            player_tick.save()


    else:
        response_message["result"] = "You have already moved this round"
        response_complete_json = {"type": "resource_complete_response",
                                  "response_message": response_message}
        message.reply_channel.send({"text": json.dumps(response_complete_json)})


def security_resource_activate(player_pk, security_resource_pk, message):
    response_message = {}
    player = Player.objects.get(id=player_pk)
    player_tick = PlayerTick(player=player, tick_number=player.game.ticks)
    if player.can_move:
        if player.manager_sanctioned:
            response_message[
                "result"] = "You have been sanctioned by the manager. You can only click on the 'Pass' button to pass this round."
            response_complete_json = {"type": "{}_response".format("security_resource_activate"),
                                      "response_message": response_message}

            message.reply_channel.send({"text": json.dumps(response_complete_json)})

        elif player.sanctioned:
            response_message[
                "result"] = "You have been peer sanctioned. You can only click on the 'Pass' button to pass this round."
            response_complete_json = {"type": "{}_response".format("security_resource_activate"),
                                      "response_message": response_message}

            message.reply_channel.send({"text": json.dumps(response_complete_json)})
        else:
            # update the number of finished security tasks; note the number corresponding to the one in the model
            if security_resource_pk == "blue_security":
                player.nf_blue += 1
                player.blue_status_security = True
                player.blue_status_capability = True
                player_tick.action = SECURITY_BLUE

            elif security_resource_pk == "red_security":
                player.nf_red += 1
                player.red_status_capability = True
                player.red_status_security = True
                player_tick.action = SECURITY_RED

            else:  # for yellow, classification = 3; there is no need to consider "lab" resource_classifications
                player.nf_yellow += 1
                player.yellow_status_security = True
                player.yellow_status_capability = True
                player_tick.action = SECURITY_YELLOW

            player.update_player_payload(response_message)
            player.save()

            response_message[
                'result'] = security_resource_pk.split("_")[0].title() + ' Security Resources Fixed!'
            response_message["active"] = True
            response_message['clicked_resource'] = security_resource_pk
            response_complete_json = {"type": "{}_response".format("security_resource_activate"),
                                      "response_message": response_message}

            message.reply_channel.send({"text": json.dumps(response_complete_json)})

            # End players move
            player_tick.save()

    else:
        response_message["result"] = "You have already moved this round"
        # return response_message
        response_message['clicked_resource'] = security_resource_pk
        response_complete_json = {"type": "{}_response".format("security_resource_activate"),
                                  "response_message": response_message}

        message.reply_channel.send({"text": json.dumps(response_complete_json)})


def player_sanction(sanctioner_pk, sanctionee_pk):
    sanctioner = Player.objects.get(pk=sanctioner_pk)
    response_message = {}
    if sanctioner.can_move:
        if sanctioner.manager_sanctioned:
            response_message[
                "result"] = "You have been sanctioned by the manager. You can only click on the 'Pass' button to pass this round."
            return response_message
        elif sanctioner.sanctioned:
            response_message[
                "result"] = "You have been peer sanctioned. You can only click on the 'Pass' button to pass this round."
            return response_message
        else:
            # TODO: Add check if sanctionee has been already peer sanctioned or manager sanctioned
            # TODO: Notify other players about status and score update

            sanctionee = Player.objects.get(pk=sanctionee_pk)

            if not sanctionee.manager_sanctioned:
                player_tick = PlayerTick(player=sanctioner, tick_number=sanctioner.game.ticks)
                player_tick.action = SANCTION
                game_tick = sanctioner.game.game_tick

                Sanction.create(sanctioner, sanctionee, game_tick)
                response_message["sanctioned"] = True
                response_message['result'] = "You have Sanctioned " + apnumber(
                    sanctionee.user.username).capitalize()
                player_tick.save()
                content = "{} has Sanctioned {} for tick:{}".format(sanctioner.name.title(), sanctionee.name.title(),
                                                                    sanctioner.game.ticks + 1)
                message = Message(content=content, game=sanctioner.game, tick=sanctioner.game.game_tick,
                                  created_by=None)
                message.save()
            else:
                response_message["sanctioned"] = False
                response_message['result'] = "{} is Already Manager Sanctioned".format(sanctionee.name.title())

            return response_message
    else:
        response_message["result"] = "You have already moved this round."
        return response_message


def pass_round(player_pk):
    player = Player.objects.get(id=player_pk)
    player_tick = PlayerTick(player=player, tick_number=player.game.ticks)
    response_message = {}
    if player.can_move:
        if player.manager_sanctioned:

            vulnerabilities_fixed = ""
            if player.sanctionee_by_manager.latest("tick_number").tick_number == player.game.ticks:
                if not player.blue_status_security:
                    response_message["resource"] = "blue"
                    player.blue_status_security = True
                    player.blue_status_capability = True
                    player.save()
                    vulnerabilities_fixed += "Blue"
                    response_message['result'] = "You've fixed {} Immunity".format(vulnerabilities_fixed)
                    response_message['resource'] = vulnerabilities_fixed
                if not player.red_status_security:
                    response_message["resource"] = "red"
                    player.red_status_security = True
                    player.red_status_capability = True
                    player.save()
                    vulnerabilities_fixed += " Red"
                    response_message['result'] = "You've fixed {} Immunity".format(vulnerabilities_fixed)
                    response_message['resource'] = vulnerabilities_fixed
                if not player.yellow_status_security:
                    response_message["resource"] = "yellow"
                    player.yellow_status_security = True
                    player.yellow_status_capability = True
                    player.save()
                    vulnerabilities_fixed += " Yellow"
                    response_message['result'] = "You've fixed {} Immunity".format(vulnerabilities_fixed)
                    response_message['resource'] = vulnerabilities_fixed
            else:
                response_message['resource'] = "null"
                response_message['result'] = "You've clicked pass."

            player_tick.action = PASS
            player_tick.save()

            return response_message
        elif player.sanctioned:
            player_tick.action = PASS
            player_tick.save()
            response_message = {'resource': "null", 'result': "You've clicked pass."}
            return response_message
        else:
            print "Something wrong. You shouldn't see the pass button if you are not sanctioned by the manager."
            response_message["result"] = "What?! You should not see the pass button now."
    else:
        response_message["result"] = "You have already moved this round."
        return response_message


def ws_add(message):
    message.reply_channel.send({"accept": True})
    Group("players").add(message.reply_channel)


# Connected to websocket.receive
# @enforce_ordering
def ws_message(message):
    message_text = json.loads(message.content['text'])
    type_of_request = message_text['type']
    if type_of_request == 'add_player':
        player_pk = message_text.get("player_pk")
        Group(str(player_pk)).add(message.reply_channel)

    if type_of_request == 'resource_complete':
        player_pk = message_text.get("player_pk")
        resource_type = message_text.get("resource_type")
        resource_position = message_text.get("resource_position")
        resource_complete(player_pk, resource_type, resource_position, message)

    elif type_of_request == 'security_resource_activate':
        player_pk = message_text.get("player_pk")
        security_resource_pk = message_text.get("security_resource_pk")
        security_resource_activate(player_pk, security_resource_pk, message)

    elif type_of_request == 'player_sanction':
        sanctioner_pk = message_text.get("sanctioner_pk")
        sanctionee_pk = message_text.get("sanctionee_pk")
        response_message = player_sanction(sanctioner_pk, sanctionee_pk)
        response_complete = {"type": "player_sanction_response", "response_message": response_message}
        message.reply_channel.send({"text": json.dumps(response_complete)})

    elif type_of_request == 'pass_button':
        player_pk = message_text.get("player_pk")
        response_message = pass_round(player_pk)
        response_complete = {"type": "{}_response".format(type_of_request), "response_message": response_message}
        message.reply_channel.send({"text": json.dumps(response_complete)})


# Connected to websocket.disconnect
def ws_disconnect(message):
    # message_text = json.loads(message.content['text'])
    # player_pk = message_text.get("player_pk")
    Group("players").discard(message.reply_channel)
    # Group(player_pk).add(message.reply_channel)
