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
            self.Sql_obj.quit_room_delete(player_id)
        elif act == '4':
            player_info = self.Sql_obj.get_individual_status(player_id)
            if player_info[0][2] == 'Owner':
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
        self.vote(id_to_act_on,sender_qq)
        if self.Sql_obj.get_voting_finishing_status(room_number):
            self.eliminate(room_number)
        survivors = self.Sql_obj.get_surviving_players(room_number)
        if len(survivors) == 2:
            print("Game ended,survirors are:")
            print(survivors)
            return

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
        
    
    def eliminate(self,room_number):
        self.Sql_obj.eliminate_update(room_number)
        self.Sql_obj.reset_vote_update(room_number)
#    def game_start(self,room_number):
#        if self.Sql_obj.check_avail(room_number) == "Room is full":


        
