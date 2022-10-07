#coding:gbk
from Sql import *
from APIClass import *
class Werewolf_kill:
    def game_progress(self,room_number,sender_qq,id_to_act_on):
        '''geme_stage = "werewolf""prophet""hunter""vote"'''
        tmp = self.Sql_obj.get_room_status_query(room_number)
        game_stage = tmp[5]
        id_to_act_on_info = self.Sql_obj.get_individual_status_by_id_and_room_number(id_to_act_on,room_number)
        sender_info = self.Sql_obj.get_individual_status(sender_qq)
        if id_to_act_on_info != "No such player":
            if id_to_act_on_info[3] == "True":
                print("Can't do anything with a player already out")
                API.send("Can't do anything with a player already out","private",API.user_id)
                return
            if sender_info[3] == "True":
                print("Sorry,you're already out")
                API.send("Sorry,you're already out","private",API.user_id)
            if game_stage == "vote":
                self.vote(id_to_act_on,sender_qq,room_number)
                if self.Sql_obj.get_voting_finishing_status(room_number):
                    self.eliminate(room_number)
                self.check_game_end(room_number)
            elif game_stage == "werewolf":
                res = self.Sql_obj.get_individual_status(sender_qq)
                if res[9] == "werewolf":
                    self.killed_by_werewolf(id_to_act_on,room_number)
                    self.Sql_obj.set_room_status_update(room_number,"killed_last_night",str(id_to_act_on))
                    if self.Sql_obj.check_game_role_living_query("prophet",room_number) > 0:
                        self.Sql_obj.set_room_status_update(room_number,"game_stage","prophet")
                    else:
                        res_room = self.Sql_obj.get_room_status_query(room_number)
                        res_player = self.Sql_obj.get_individual_status_by_id_and_room_number(res_room[6],room_number)
                        if res_player[9] == "hunter":
                            self.Sql_obj.set_room_status_update(room_number,"game_stage","hunter")
                        else:
                            self.Sql_obj.set_room_status_update(room_number,"game_stage","vote")
                else:
                    print("You are not the werewolf!")
                    API.send("You are not the werewolf!","private",API.user_id)
                self.check_game_end(room_number)
            elif game_stage == "prophet":
                res = self.Sql_obj.get_individual_status(sender_qq)
                if res[9] == "prophet":
                    player_info = self.Sql_obj.get_individual_status_by_id_and_room_number(id_to_act_on,room_number)
                    if player_info[9] == 'werewolf':
                        print("No."+id_to_act_on+" is a werewolf")
                        API.send("No."+id_to_act_on+" is a werewolf","private",API.user_id)
                    else:
                        print("No."+id_to_act_on+" is good")    
                        API.send("No."+id_to_act_on+" is good","private",API.user_id)
                    self.prophet_inquired(sender_qq,room_number)
                else:
                    print("You are not the prophet!")
                    API.send("You are not the prophet!","private",API.user_id)
                self.check_game_end(room_number)
            elif game_stage == "hunter":
                res = self.Sql_obj.get_individual_status(sender_qq)
                if res[9] == "hunter":
                    self.killed_by_werewolf(id_to_act_on,room_number)
                    self.Sql_obj.set_room_status_update(room_number,"killed_last_night",id_to_act_on)
                    self.Sql_obj.set_room_status_update(room_number,"game_stage","vote")
                else:
                    print("You are not the hunter!")
                    API.send("You are not the hunter!","private",API.user_id)
                self.check_game_end(room_number)
            else:
                pass
        else:
            print("No such player!")
            API.send("No such player!","private",API.user_id)

    def resp_to_data(self,act,room_number,player_name,player_id,room_size,id_to_act_on,num_werewolf,num_villager,num_hunter,num_prophet):
        '''[Connect to Message_handling.py] act:Enter-1,Create-2,Quit-3,Start game-4,Gaming_input-5(input as char)'''
        if act == '1':
            self.Sql_obj.enter_room_add(str(player_name),str(room_number),str(player_id),'0')
            self.Sql_obj.in_room_update(room_number)
        elif act == '2':
            self.Sql_obj.enter_room_add(str(player_name),str(room_number),str(player_id),str(room_size))
            self.Sql_obj.in_room_update(room_number)
        elif act == '3':
            player_info = self.Sql_obj.get_individual_status(player_id)
            if player_info[2] == 'Owner':
                self.Sql_obj.end_game(room_number)
            else:
                self.Sql_obj.quit_room_delete(player_id)
                self.Sql_obj.in_room_update(room_number)
        elif act == '4':
            player_info = self.Sql_obj.get_individual_status(player_id)
            if player_info[2] == 'Owner':
                if self.Sql_obj.check_avail(room_number) == "Room is full":
                    self.Sql_obj.update_roomstatus(room_number,'True')
                    room_info = self.Sql_obj.get_room_status_query(room_number)
                    if str(int(num_werewolf) + int(num_prophet) + int(num_hunter) + int(num_villager)) != room_info[1]:
                        print("INPUT_ERROR")
                        API.send("Please input the numbers correctly","private",API.user_id)
                        return
                    elif num_werewolf == "0" or num_villager == "0":
                        print("ROLES_IMPROPER")
                        API.send("There must be at least ONE werewolf and ONE villager","private",API.user_id)
                    else:
                        self.Sql_obj.id_assign_update(room_number)
                        self.Sql_obj.game_role_assign(room_number,int(num_werewolf),int(num_villager),int(num_hunter),int(num_prophet))
                        self.Sql_obj.set_room_status_update(room_number,"game_stage","werewolf")
                        print("Game start authorized")
                        self.send_pri_by_group(room_number,"Game Started")
                        self.Sql_obj.in_room_update(room_number)
                elif self.Sql_obj.check_avail(room_number) == "Game started":
                    print("Game has already started")
                    API.send("Game has already started","private",API.user_id)
                else:
                    print("Sorry,not enough people")
                    API.send("Sorry,not enough people","private",API.user_id)
            else:
                print("Sorry,you're not the owner")
                API.send("Sorry,you're not the owner","private",API.user_id)
        else:#normal gaming
            self.game_progress(room_number,player_id,id_to_act_on)

    def __init__(self,password):
        self.Sql_obj=Sql(password,'127.0.0.2','root','ydebot','gbk')
    

    def check_player_in_game(self,player_qq):
        return self.Sql_obj.check_player_in_game_query(player_qq)

    def vote(self,id_to_vote,voter_qq,room_number):
        voter_info = self.Sql_obj.get_individual_status(voter_qq)
        if voter_info[3] == "True":#eliminated
            print("ID "+voter_info[6]+" is out")
            self.send_pri_by_group(room_number,"ID "+voter_info[6]+" is out")
            self.Sql_obj.survivors_update(room_number)
            return
        if voter_info[8] == "True":#voted
            print("ID "+voter_info[6]+" has already voted")
            API.send("You have already voted!","private",API.user_id)
            return
        #haven't voted or elimated
        
        self.Sql_obj.vote_update(id_to_vote,voter_info[7],voter_info[4])
        
    def prophet_inquired(self,id_of_prophet,room_number):
        res = self.Sql_obj.get_individual_status(id_of_prophet)
        if res[3] == "True":
            print("No."+id_of_prophet+" is out")
            API.send("You're already out!","private",API.user_id)
        else:
            self.Sql_obj.prophet_inquired_update(id_of_prophet,room_number)
            if self.Sql_obj.prophet_finished_query(room_number):
                res_room = self.Sql_obj.get_room_status_query(room_number)
                res_player = self.Sql_obj.get_individual_status_by_id_and_room_number(res_room[6],room_number)
                if res_player[9] == "hunter":
                    self.Sql_obj.set_room_status_update(room_number,"game_stage","hunter")
                else:
                    self.Sql_obj.set_room_status_update(room_number,"game_stage","vote")

                self.Sql_obj.reset_vote_update(room_number,"False")
            else:
                pass

    def player_list_gen(self,room_number):
        '''return a list of player_ids in the room'''
        res = self.Sql_obj.get_player_list_query(room_number)
        player_ids = []
        for i in range(0,len(res)):
            player_ids.append(res[i][6])
        return player_ids


    def send_pri_by_group(self,room_number,msg):
        user_ids = self.player_list_gen(room_number)
        API.send_privately_by_group(user_ids,msg)

    def killed_by_werewolf(self,id_to_act_on,room_number):
        '''set is_out as "True"'''
        self.Sql_obj.killed_by_werewolf_update(id_to_act_on,room_number)
        return

    def eliminate(self,room_number):
        res = self.Sql_obj.eliminate_update(room_number)
        if res == "Elimination finished":
            self.Sql_obj.set_room_status_update(room_number,"game_stage","werewolf")
        else:
            self.Sql_obj.set_room_status_update(room_number,"game_stage","vote")
        return

    def check_game_end(self,room_number):
        res = self.Sql_obj.check_game_end_query(room_number)
        if res == "Game continue":
            pass
        else:
            print(res)
            self.Sql_obj.reset_isout_update(room_number)
#    def game_start(self,room_number):
#        if self.Sql_obj.check_avail(room_number) == "Room is full":


        
