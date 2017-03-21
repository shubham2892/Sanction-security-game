import json

from channels import Group
from django.contrib.humanize.templatetags.humanize import apnumber

from Game.models import Player, PlayerTick, ResearchResource, RESEARCH_TASK, RESEARCH_OBJ, Statistics, SecurityResource, \
    SECURITY, Capabilities, Tick, Sanction, SANCTION, PASS, Message


def resource_complete(player_pk, resource_pk):
    player = Player.objects.get(id=player_pk)
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
            research_resource = ResearchResource.objects.get(pk=resource_pk)
            capable = player.capabilities.security_resources.get(classification=research_resource.classification)
            if capable.active:
                research_resource.complete = True
                research_resource.save()

                # Record Player's action as "Research Task"
                player_tick.action = RESEARCH_TASK

            else:
                response_message[
                    "result"] = "You are not capable of completing this task. Make sure you patch your vulnerabilities."
                return response_message

            objective_completed = True
            objective = research_resource.researchobjective_set.all().first()
            for resource in objective.research_resources.all():
                if resource.complete == False:
                    objective_completed = False

            response_message['result'] = str(research_resource) + ' Completed!'

            if objective_completed:
                objective.complete = True

                # Record Player's action as "Research Objective"
                player_tick.action = RESEARCH_OBJ

                player = objective.player
                player.score += objective.value
                # update number of finished research tasks; note the number corresponding to the one in the model
                if objective.name == 1:
                    player.nf_workshop += 1
                elif objective.name == 2:
                    player.nf_conference += 1
                else:
                    player.nf_journal += 1

                player.save()
                update_player(player)
                objective.save()
                response_message['result'] = str(objective) + " Completed!"
            # End players move
            player_tick.save()

            if objective_completed:
                # update Statistics table data; note the number corresponding to the one in the model
                stats = Statistics(game=player.game, player=player, player_tick=player_tick)
                if objective.name == 1:  # workshop
                    stats.nf_finished_task = player.nf_workshop
                    stats.type_of_task = 0
                elif objective.name == 2:  # conference
                    stats.nf_finished_task = player.nf_conference
                    stats.type_of_task = 1
                else:  # ==3: journal
                    stats.nf_finished_task = player.nf_journal
                    stats.type_of_task = 2
                # print stats
                stats.save()

            response_message['pk'] = research_resource.pk
            response_message['resource_complete'] = research_resource.complete
            response_message['objective_complete'] = objective_completed
            response_message['score'] = player.score

            # TODO Notify other players about updated score and status
            return response_message
    else:
        response_message["result"] = "You have already moved this round"
        return response_message


def security_resource_activate(player_pk, security_resource_pk):
    response_message = {}
    player = Player.objects.get(id=player_pk)
    player_tick = PlayerTick(player=player, tick=player.game.current_tick)
    if player.can_move:
        if player.manager_sanctioned:
            response_message[
                "result"] = "You have been sanctioned by the manager. You can only click on the 'Pass' button to pass this round."
            return response_message
        if player.sanctioned:
            response_message[
                "result"] = "You have been peer sanctioned. You can only click on the 'Pass' button to pass this round."
            return response_message
        else:
            security_resource = SecurityResource.objects.get(pk=security_resource_pk)
            security_resource.active = True
            security_resource.save()

            # update the number of finished security tasks; note the number corresponding to the one in the model
            if security_resource.classification == 1:
                player.nf_blue += 1
            elif security_resource.classification == 2:
                player.nf_red += 1
            else:  # for yellow, classification = 3; there is no need to consider "lab" resource_classifications
                player.nf_yellow += 1

            player.save()
            update_player(player)
            # print "the resource is "
            # print security_resource.classification
            # Record players action as "Security"
            player_tick.action = SECURITY

            # After security resource is activated, reactivate capability if necessary
            c = Capabilities.objects.get(player=player).security_resources.get(
                classification=security_resource.classification)
            c.active = True
            c.save()

            # End players move
            print "Saving ticket 3"
            player_tick.save()

            # update Statistics table data; note the number corresponding to the one in the model
            stats = Statistics(game=player.game, player=player, player_tick=player_tick)
            if security_resource.classification == 1:  # blue
                stats.nf_finished_task = player.nf_blue
                stats.type_of_task = 5
            elif security_resource.classification == 2:  # red
                stats.nf_finished_task = player.nf_red
                stats.type_of_task = 3
            else:  # for yellow, classification = 3
                stats.nf_finished_task = player.nf_yellow
                stats.type_of_task = 4
            # print stats
            stats.save()

            response_message['result'] = str(security_resource) + ' Activated!  ' + str(
                security_resource.get_classification_display().capitalize()) + ' capability restored.'

            response_message['pk'] = security_resource.pk
            response_message['active'] = security_resource.active
            return response_message
    else:
        response_message["result"] = "You have already moved this round"
        return response_message


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
                content = "{} has sanctioned {} for tick:{}".format(sanctioner.name, sanctionee.name, sanction.tick_number)
                message = Message(content=content, game=sanctioner.game, tick=sanctioner.game.current_tick, created_by=None)
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
            player.counter += 1
            vulnerabilities_fixed = ""
            if player.sanctionee_by_manager.latest("tick_number").tick_number == player.game.current_tick.number:
                if not player.blue_status:
                    response_message["resource"] = "blue"
                    player.blue_status = True

                    for vulnerability in player.vulnerabilities.security_resources.filter(classification=1):
                        vulnerability.active = True
                        vulnerability.save()
                    player.nf_blue += 1
                    player.save()
                    update_player(player)
                    for capability in player.capabilities.security_resources.filter(classification=1):
                        capability.active = True
                        capability.save()

                    # stats.nf_finished_task = player.nf_blue
                    # stats.type_of_task = 5
                    vulnerabilities_fixed += "blue"
                    response_message['result'] = "You've fixed {} vulnerability".format(vulnerabilities_fixed)
                    response_message['resource'] = vulnerabilities_fixed
                if not player.red_status:
                    response_message["resource"] = "red"
                    player.red_status = True
                    for vulnerability in player.vulnerabilities.security_resources.filter(classification=2):
                        vulnerability.active = True
                        vulnerability.save()

                    player.nf_red += 1
                    player.save()
                    update_player(player)

                    for capability in player.capabilities.security_resources.filter(classification=2):
                        capability.active = True
                        capability.save()

                    # stats.nf_finished_task = player.nf_red
                    # stats.type_of_task = 3
                    vulnerabilities_fixed += " red"
                    response_message['result'] = "You've fixed {} vulnerability".format(vulnerabilities_fixed)
                    response_message['resource'] = vulnerabilities_fixed
                if not player.yellow_status:
                    response_message["resource"] = "yellow"
                    player.yellow_status = True
                    for vulnerability in player.vulnerabilities.security_resources.filter(classification=3):
                        vulnerability.active = True
                        vulnerability.save()

                    player.nf_yellow += 1
                    player.save()
                    update_player(player)

                    for capability in player.capabilities.security_resources.filter(classification=3):
                        capability.active = True
                        capability.save()

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

            if player.counter == player.counter_sum:
                player.counter = 0
                player.counter_sum = 0
                player.save()

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

    player_update_dict["vulnerabilities"] = []
    for vulnerability in player.vulnerabilities.security_resources.all():
        player_update_dict["vulnerabilities"].append(
            {"active": vulnerability.active, "classification_display": vulnerability.get_classification_display()})

    player_update_dict["type"] = "player_update"

    Group("players").send({"text": json.dumps(player_update_dict)})


# Connected to websocket.receive
def ws_message(message):
    message_text = json.loads(message.content['text'])
    type_of_request = message_text['type']
    if type_of_request == 'add_player':
        player_pk = message_text.get("player_pk")
        print "Player added:{}".format(player_pk)
        Group(str(player_pk)).add(message.reply_channel)

    if type_of_request == 'resource_complete':
        player_pk = message_text.get("player_pk")
        resource_pk = message_text.get("resource_pk")
        response_message = resource_complete(player_pk, resource_pk)
        response_message['clicked_resource'] = resource_pk
        response_complete = {"type": "{}_response".format(type_of_request), "response_message": response_message}
        message.reply_channel.send({"text": json.dumps(response_complete)})

    elif type_of_request == 'security_resource_activate':
        player_pk = message_text.get("player_pk")
        security_resource_pk = message_text.get("security_resource_pk")
        response_message = security_resource_activate(player_pk, security_resource_pk)
        response_complete = {"type": "{}_response".format(type_of_request), "response_message": response_message}
        message.reply_channel.send({"text": json.dumps(response_complete)})

    elif type_of_request == 'player_sanction':
        sanctioner_pk = message_text.get("sanctioner_pk")
        sanctionee_pk = message_text.get("sanctionee_pk")
        tick_pk = message_text.get("tick_pk")
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

