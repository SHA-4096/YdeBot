#coding:gbk
from Sql import *

class Werewolf_kill:
    def resp_to_data(self,act,room_number,player_name,player_id,room_size,id_to_act_on):
        '''[Connect to Message_handling.py] act:Enter-1,Create-2,Quit-3,Start game-4,Gaming_input-5(input as char)'''
        if act == '1':
            self.Sql_obj.enter_room_add(str(player_name),str(room_number),str(player_id),'0')
        elif act == '2':
            self.Sql_obj.enter_room_add(str(player_name),str(room_number),str(player_id),str(room_size))
        elif act == '3':
            player_info = self.Sql_obj.get_individual_status(player_id)
            if player_info[2] == 'Owner':
                self.Sql_obj.end_game(room_number)
            else:
                self.Sql_obj.quit_room_delete(player_id)
        elif act == '4':
            player_info = self.Sql_obj.get_individual_status(player_id)
            if player_info[2] == 'Owner':
                if self.Sql_obj.check_avail(room_number) == "Room is full":
                    self.Sql_obj.update_roomstatus(room_number,'True')
                    return
                else:
                    print("Sorry,not enough people")
                    return
            else:
                print("Sorry,you're not the owner")
        else:#normal gaming
            self.game_progress(room_number,player_id,id_to_act_on)

    def game_progress(self,room_number,sender_qq,id_to_act_on):
        '''geme_stage = "werewolf""prophet""hunter""vote"'''
        tmp = self.Sql_obj.get_room_status_query(room_number)
        game_stage = tmp[5]
        id_to_act_on_info = self.Sql_obj.get_individual_status_by_id_and_room_number(id_to_act_on,room_number)
        sender_info = self.Sql_obj.get_individual_status(sender_qq)
        if id_to_act_on_info != "No such player":
            if id_to_act_on_info[3] == "True":
                print("Can't do anything with a player already out")
                return
            if sender_info[3] == "True":
                print("Sorry,you're already out")
            if game_stage == "vote":
                self.vote(id_to_act_on,sender_qq)
                if self.Sql_obj.get_voting_finishing_status(room_number):
                    self.eliminate(room_number)
                    self.Sql_obj.set_room_status_update(room_number,"game_stage","werewolf")
                survivors = self.Sql_obj.get_surviving_players(room_number)
                print(survivors)
                '''
                if len(survivors) == 2:
                    self.Sql_obj.reset_isout_update(room_number)
                    print("Game ended,survirors are:")
                    print(survivors)
                '''
                self.check_game_end(room_number)
            elif game_stage == "werewolf":
                res = self.Sql_obj.get_individual_status(sender_qq)
                if res[9] == "werewolf":
                    self.killed_by_werewolf(id_to_act_on,room_number)
                    self.Sql_obj.set_room_status_update(room_number,"killed_last_night",str(id_to_act_on))
                    if self.Sql_obj.check_game_role_living_query("prophet",room_number) > 0:
                        self.Sql_obj.set_room_status_update(room_number,"game_stage","prophet")
                    else:
                        if self.Sql_obj.check_game_role_living_query("hunter",room_number) > 0:
                            self.Sql_obj.set_room_status_update(room_number,"game_stage","hunter")
                        else:
                            self.Sql_obj.set_room_status_update(room_number,"game_stage","vote")
                else:
                    print("You are not the werewolf!")
                self.check_game_end(room_number)
            elif game_stage == "prophet":
                res = self.Sql_obj.get_individual_status(sender_qq)
                if res[9] == "prophet":
                    player_info = self.Sql_obj.get_individual_status_by_id_and_room_number(id_to_act_on,room_number)
                    if player_info[9] == 'werewolf':
                        print("No."+id_to_act_on+" is a werewolf")
                    else:
                        print("No."+id_to_act_on+" is good")    
                    self.prophet_inquired(sender_qq,room_number)
                else:
                    print("You are not the prophet!")
                self.check_game_end(room_number)
            elif game_stage == "hunter":
                res = self.Sql_obj.get_individual_status(sender_qq)
                if res[9] == "hunter":
                    self.killed_by_werewolf(id_to_act_on,room_number)
                    self.Sql_obj.set_room_status_update(room_number,"killed_last_night",id_to_act_on)
                    self.Sql_obj.set_room_status_update(room_number,"game_stage","vote")
                else:
                    print("You are not the hunter!")
                self.check_game_end(room_number)
            else:
                pass
        else:
            print("No such player!")
    def DEBUG_resp_to_data(self,act,room_number,player_name,player_id,room_size,id_to_act_on):
        '''[Connect to Message_handling.py] act:Enter-1,Create-2,Quit-3,Start game-4,Gaming_input-5(input as char)'''
        if act == '1':
            self.Sql_obj.enter_room_add(str(player_name),str(room_number),str(player_id),'0')
        elif act == '2':
            self.Sql_obj.enter_room_add(str(player_name),str(room_number),str(player_id),str(room_size))
        elif act == '3':
            player_info = self.Sql_obj.get_individual_status(player_id)
            if player_info[2] == 'Owner':
                self.Sql_obj.end_game(room_number)
            else:
                self.Sql_obj.quit_room_delete(player_id)
        elif act == '4':
            player_info = self.Sql_obj.get_individual_status(player_id)
            if player_info[2] == 'Owner':
                if self.Sql_obj.check_avail(room_number) == "Room is full":
                    self.Sql_obj.update_roomstatus(room_number,'True')
                    print("Game start authorized")
                    return
                else:
                    print("Sorry,not enough people")
                    return
            else:
                print("Sorry,you're not the owner")
        else:#normal gaming
            self.game_progress(room_number,player_id,id_to_act_on)


            '''
            survivors = self.Sql_obj.get_surviving_players(room_number)
            if len(survivors) == 2:
                print("Game ended,survirors are:")
                print(survivors)
                return
            if self.Sql_obj.get_voting_finishing_status(room_number):
                self.eliminate(room_number)
                return
            else:
                voter_qq = input("Who are U:")
                id_to_vote = input("Who will U vote:")
                self.vote(id_to_vote,voter_qq)
                return
'''
            
    def __init__(self,password):
        self.Sql_obj=Sql(password,'127.0.0.2','root','ydebot','gbk')
    
    def enter_room(self):#for debugging
        '''for debugging'''
        rooms = self.Sql_obj.get_avail_rooms()
        while True:
            print(rooms)
            act = input("Enter-1,Create-2,Quit-3,Stop_adding-4:")
            if act == '1':
                room_number = input('Room_number:')
                player_name = input('nickname:')
                player_id = input('qq:') 
                self.Sql_obj.enter_room_add(str(player_name),str(room_number),str(player_id),'0')
            elif act == '2':
                room_number = input('Room_number:')
                player_name = input('nickname:')
                player_id = input('qq:') 
                room_size = input("size:")
                self.Sql_obj.enter_room_add(str(player_name),str(room_number),str(player_id),str(room_size))
            elif act == '3':
                player_id = input('qq:') 
                self.Sql_obj.quit_room_delete(player_id)
            else:
                self.game_start("123456")

    def check_player_in_game(self,player_qq):
        return self.Sql_obj.check_player_in_game_query(player_qq)

    def game_start(self,room_number):
        '''for debugging'''
        self.Sql_obj.id_assign_update(room_number)
        while True:
            survivors = self.Sql_obj.get_surviving_players(room_number)
            if len(survivors) == 2:
                print("Game ended,survirors are:")
                print(survivors)
                break
            if self.Sql_obj.get_voting_finishing_status(room_number):
                self.eliminate(room_number)
            else:
                voter_qq = input("Who are U:")
                id_to_vote = input("Who will U vote:")
                self.vote(id_to_vote,voter_qq)

    def vote(self,id_to_vote,voter_qq):
        voter_info = self.Sql_obj.get_individual_status(voter_qq)
        if voter_info[3] == "True":#eliminated
            print("ID "+voter_info[6]+" is out")
            return
        if voter_info[8] == "True":#voted
            print("ID "+voter_info[6]+" has already voted")
            return
        #haven't voted or elimated
        self.Sql_obj.vote_update(id_to_vote,voter_info[7],voter_info[4])
        
    def prophet_inquired(self,id_of_prophet,room_number):
        res = self.Sql_obj.get_individual_status(id_of_prophet)
        if res[3] == "True":
            print("No."+id_of_prophet+" is out")
        else:
            self.Sql_obj.prophet_inquired_update(id_of_prophet,room_number)
            if self.Sql_obj.prophet_finished_query(room_number):
                res_room = self.Sql_obj.get_room_status_query(room_number)
                res_player = self.Sql_obj.get_individual_status_by_id_and_room_number(res_room[6],room_number)
                if res_player[9] == "hunter":
                    if self.Sql_obj.check_game_role_living_query("hunter",room_number) >0 :
                        self.Sql_obj.set_room_status_update(room_number,"game_stage","hunter")
                else:
                    self.Sql_obj.set_room_status_update(room_number,"game_stage","vote")
                    print("game_stage has been set to vote")
                self.Sql_obj.reset_vote_update(room_number,"False")
            else:
                pass
        

    def killed_by_werewolf(self,id_to_act_on,room_number):
        '''set is_out as "True"'''
        self.Sql_obj.killed_by_werewolf_update(id_to_act_on,room_number)
        return

    def eliminate(self,room_number):
        self.Sql_obj.eliminate_update(room_number)
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


        
