#coding:gbk
from Sql import *

class Werewolf_kill:
    Sql_obj = None
    def __init__(self,password):
        self.Sql_obj=Sql(password,'127.0.0.2','root','ydebot','gbk')
    
    def enter_room(self):#for debugging
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


        
