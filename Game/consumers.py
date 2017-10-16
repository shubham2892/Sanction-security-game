import json
import random

from channels import Group
from django.contrib.humanize.templatetags.humanize import apnumber
from django.db.models import F

from Game.models import Player, PlayerTick, RESEARCH_TASK, RESEARCH_OBJ, Statistics, SECURITY, \
    Sanction, SANCTION, PASS, Message, BLUE, RED, YELLOW, Workshop, Conference, Journal


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


def resource_complete(player_pk, resource_type, resource_position):
    player = Player.objects.select_related('game').get(id=player_pk)
    player_tick = PlayerTick(player=player, tick=player.game.current_tick)
    response_message = {}
    if player.can_move:
        if player.manager_sanctioned:
            response_message[
                "result"] = "You have been sanctioned by the manager. You can only click on the 'Pass' button to pass this round."
            return response_message
        elif player.sanctioned:
            response_message[
                "result"] = "You have been peer sanctioned. You can only click on the 'Pass' button to pass this round."
            return response_message
        else:
            research_resource = ""
            objective_completed = False
            new_classifications = []
            NOT_CAPABLE_ERROR_MESSAGE = "You are not capable of completing this task. Make sure you patch your vulnerabilities."
            if resource_type == "workshop":
                workshop = Workshop.objects.get(player=player_pk)
                resource_classification = workshop.classification
                if not check_player_capability(resource_classification, player):
                    response_message['result'] = NOT_CAPABLE_ERROR_MESSAGE
                    return response_message
                random_number = random.randint(1, 3)
                Workshop.objects.filter(player=player_pk).update(classification=random_number, count=F('count') + 1)
                player.score += workshop.score
                objective_completed = True
                research_resource = resource_classification
                new_classifications.append(workshop.classification_display)
                player.nf_workshop += 1

            elif resource_type == 'conference':
                conference = Conference.objects.get(player=player_pk)

                print "resource position:{}".format(resource_position)
                print "Player Pk:{}".format(player.user.username)
                if resource_position == 'one':
                    resource_classification = conference.classification_one
                else:
                    resource_classification = conference.classification_two

                print "resource classificiation:{}".format(resource_classification)

                if not check_player_capability(resource_classification, player):
                    response_message['result'] = NOT_CAPABLE_ERROR_MESSAGE
                    return response_message

                if resource_position == 'one':
                    conference.complete_one = True
                else:
                    conference.complete_two = True

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
                    research_resource = resource_classification
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
                    return response_message

                if resource_position == 'one':
                    journal.complete_one = True
                elif resource_position == 'two':
                    journal.complete_two = True
                else:
                    journal.complete_three = True

                if journal.complete_one and journal.complete_two and journal.complete_three:
                    journal.classification_one = random.randint(1, 3)
                    journal.classification_two = random.randint(1, 3)
                    journal.classification_three = random.randint(1, 3)
                    journal.complete_one = False
                    journal.complete_two = False
                    journal.complete_three = False
                    player.score += journal.score
                    objective_completed = True
                    research_resource = resource_classification
                    player.nf_journal += 1
                    new_classifications.append(journal.classification_display_one)
                    new_classifications.append(journal.classification_display_two)
                    new_classifications.append(journal.classification_display_three)

                journal.save()

            response_message['result'] = str(research_resource) + ' Completed!'

            if objective_completed:
                player_tick.action = RESEARCH_OBJ
                response_message['result'] = resource_type + " Completed!"
                player_tick.save()

            # End players move
            player.save()

            if objective_completed:
                # update Statistics table data; note the number corresponding to the one in the model
                stats = Statistics(game=player.game, player=player, player_tick=player_tick)
                if resource_type == "workshop":  # workshop
                    stats.nf_finished_task = player.nf_workshop
                    stats.type_of_task = 0
                elif resource_type == "conference":  # conference
                    stats.nf_finished_task = player.nf_conference
                    stats.type_of_task = 1
                else:
                    stats.nf_finished_task = player.nf_journal
                    stats.type_of_task = 2
                # print stats
                stats.save()

            response_message['resource_complete'] = True
            response_message['objective_complete'] = objective_completed
            response_message['new_classifications'] = new_classifications
            response_message['resource_type'] = resource_type
            response_message['resource_position'] = resource_position
            response_message['score'] = player.score

            print response_message
            # TODO Notify other players about updated score and status
            return response_message
    else:
        response_message["result"] = "You have already moved this round"
        return response_message


def security_resource_activate(player_pk, security_resource_pk, message):
    response_message = {}
    player = Player.objects.get(id=player_pk)
    player_tick = PlayerTick(player=player, tick=player.game.current_tick)
    if player.can_move:
        if player.manager_sanctioned:
            response_message[
                "result"] = "You have been sanctioned by the manager. You can only click on the 'Pass' button to pass this round."
            response_complete_json = {"type": "{}_response".format("security_resource_activate"),
                                      "response_message": response_message}

            message.reply_channel.send({"text": json.dumps(response_complete_json)})

        if player.sanctioned:
            response_message[
                "result"] = "You have been peer sanctioned. You can only click on the 'Pass' button to pass this round."
            response_complete_json = {"type": "{}_response".format("security_resource_activate"),
                                      "response_message": response_message}

            message.reply_channel.send({"text": json.dumps(response_complete_json)})
        else:
            # update the number of finished security tasks; note the number corresponding to the one in the model
            if security_resource_pk == "blue_security":
                player.nf_blue += 1
                player.last_tick_blue = player.game.current_tick.number + 1
                player.blue_status_security = True
                player.blue_status_capability = True

            elif security_resource_pk == "red_security":
                player.nf_red += 1
                player.last_tick_red = player.game.current_tick.number + 1
                player.red_status_capability = True
                player.red_status_security = True

            else:  # for yellow, classification = 3; there is no need to consider "lab" resource_classifications
                player.nf_yellow += 1
                player.last_tick_yellow = player.game.current_tick.number + 1
                player.yellow_status_security = True
                player.yellow_status_capability = True

            player.update_player_payload(response_message)
            player.save()

            response_message[
                'result'] = security_resource_pk + ' Activated!  ' + security_resource_pk + ' capability restored.'
            response_message["active"] = True
            response_message['clicked_resource'] = security_resource_pk
            response_complete_json = {"type": "{}_response".format("security_resource_activate"),
                                      "response_message": response_message}

            message.reply_channel.send({"text": json.dumps(response_complete_json)})

            # update_player(player)
            player_tick.action = SECURITY

            # End players move
            player_tick.save()

            # update Statistics table data; note the number corresponding to the one in the model
            stats = Statistics(game=player.game, player=player, player_tick=player_tick)
            if security_resource_pk == "blue_security":  # blue
                stats.nf_finished_task = player.nf_blue
                stats.type_of_task = 5
            elif security_resource_pk == "red_security":  # red
                stats.nf_finished_task = player.nf_red
                stats.type_of_task = 3
            else:  # for yellow, classification = 3
                stats.nf_finished_task = player.nf_yellow
                stats.type_of_task = 4
            # print stats
            stats.save()


            # return response_message
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

            player_tick = PlayerTick(player=sanctioner, tick=sanctioner.game.current_tick)
            player_tick.action = SANCTION
            player_tick.save()
            tick = sanctioner.game.current_tick
            sanctionee = Player.objects.get(pk=sanctionee_pk)
            if not sanctionee.manager_sanctioned:
                sanction = Sanction.create(sanctioner, sanctionee, tick)
                response_message["sanctioned"] = True
                response_message['result'] = "You have sanctioned Player " + apnumber(sanctionee.number).capitalize()
                content = "{} has sanctioned {} for tick:{}".format(sanctioner.name, sanctionee.name,
                                                                    sanction.tick_number)
                message = Message(content=content, game=sanctioner.game, tick=sanctioner.game.current_tick,
                                  created_by=None)
                message.save()
            else:
                response_message["sanctioned"] = False
                response_message['result'] = "{} is already manager sanctioned".format(sanctionee.name)

            return response_message
    else:
        response_message["result"] = "You have already moved this round."
        return response_message


def pass_round(player_pk):
    # TODO: Notify other players about status and score update

    player = Player.objects.get(id=player_pk)
    player_tick = PlayerTick(player=player, tick=player.game.current_tick)
    response_message = {}
    if player.can_move:
        if player.manager_sanctioned:

            # fix security tasks if counter is odd; since we fix a security task when clicked twice
            # stats = Statistics(game=player.game, player=player, player_tick=player_tick)
            # player.counter += 1
            vulnerabilities_fixed = ""
            if player.sanctionee_by_manager.latest("tick_number").tick_number == player.game.current_tick.number:
                if not player.blue_status_security:
                    response_message["resource"] = "blue"
                    player.blue_status_security = True
                    player.blue_status_capability = True
                    # for vulnerability in player.vulnerabilities.security_resources.filter(classification=1):
                    #     vulnerability.active = True
                    #     vulnerability.save()
                    # player.nf_blue += 1
                    # player.last_tick_blue = player.game.current_tick.number + 1
                    player.save()
                    # update_player(player)
                    # for capability in player.capabilities.security_resources.filter(classification=1):
                    #     capability.active = True
                    #     capability.save()

                    # stats.nf_finished_task = player.nf_blue
                    # stats.type_of_task = 5
                    vulnerabilities_fixed += "blue"
                    response_message['result'] = "You've fixed {} vulnerability".format(vulnerabilities_fixed)
                    response_message['resource'] = vulnerabilities_fixed
                if not player.red_status_security:
                    response_message["resource"] = "red"
                    player.red_status_security = True
                    player.red_status_capability = True
                    # for vulnerability in player.vulnerabilities.security_resources.filter(classification=2):
                    #     vulnerability.active = True
                    #     vulnerability.save()
                    #
                    # player.nf_red += 1
                    # player.last_tick_red = player.game.current_tick.number + 1
                    player.save()
                    # update_player(player)

                    # for capability in player.capabilities.security_resources.filter(classification=2):
                    #     capability.active = True
                    #     capability.save()
                    #
                    # stats.nf_finished_task = player.nf_red
                    # stats.type_of_task = 3
                    vulnerabilities_fixed += " red"
                    response_message['result'] = "You've fixed {} vulnerability".format(vulnerabilities_fixed)
                    response_message['resource'] = vulnerabilities_fixed
                if not player.yellow_status_security:
                    response_message["resource"] = "yellow"
                    player.yellow_status_security = True
                    player.yellow_status_capability = True
                    # for vulnerability in player.vulnerabilities.security_resources.filter(classification=3):
                    #     vulnerability.active = True
                    #     vulnerability.save()
                    # player.last_tick_yellow = player.game.current_tick.number + 1
                    # player.nf_yellow += 1
                    player.save()
                    # update_player(player)

                    # for capability in player.capabilities.security_resources.filter(classification=3):
                    #     capability.active = True
                    #     capability.save()

                    # stats.nf_finished_task = player.nf_yellow
                    # stats.type_of_task = 4
                    vulnerabilities_fixed += " yellow"
                    response_message['result'] = "You've fixed {} vulnerability".format(vulnerabilities_fixed)
                    response_message['resource'] = vulnerabilities_fixed
                    # stats.save()
                    # print stats
            else:
                response_message['resource'] = "null"
                response_message['result'] = "You've clicked pass."

            player_tick.action = PASS
            player_tick.save()

            # if player.counter == player.counter_sum:
            #     player.counter = 0
            #     player.counter_sum = 0
            #     player.save()

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


def update_player(player):
    player_update_dict = {"id": player.id, "score": player.score}
    if player.sanctioned:
        player_update_dict["status"] = "Sanctioned"
    else:
        player_update_dict["status"] = "Thinking.."

    # Append Blue Security
    player_update_dict["blue_security"] = {"active": player.blue_status_security,
                                           "deadline_sanction": player.deadline_sanction_blue}

    # Append Red Security
    player_update_dict["red_security"] = {"active": player.red_status_security,
                                          "deadline_sanction": player.deadline_sanction_red}

    # Append Yellow Security
    player_update_dict["yellow_security"] = {"active": player.yellow_status_security,
                                             "deadline_sanction": player.deadline_sanction_yellow}

    player_update_dict["blue_capability"] = player.blue_status_capability
    player_update_dict["red_capability"] = player.red_status_capability
    player_update_dict["yellow_capability"] = player.yellow_status_capability

    player_update_dict["type"] = "player_update"

    Group("players").send({"text": json.dumps(player_update_dict)})


# Connected to websocket.receive
# @enforce_ordering
def ws_message(message):
    message_text = json.loads(message.content['text'])
    type_of_request = message_text['type']
    if type_of_request == 'add_player':
        player_pk = message_text.get("player_pk")
        Group(str(player_pk)).add(message.reply_channel)

    if type_of_request == 'resource_complete':
        print "Request Received"
        player_pk = message_text.get("player_pk")
        resource_type = message_text.get("resource_type")
        resource_position = message_text.get("resource_position")
        response_message = resource_complete(player_pk, resource_type, resource_position)
        response_complete_json = {"type": "{}_response".format(type_of_request), "response_message": response_message}
        message.reply_channel.send({"text": json.dumps(response_complete_json)})

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
