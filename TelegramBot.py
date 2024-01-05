from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
import time
import os
class TelegramBot:
    def __init__(self, api_id, api_hash, phone):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_file = f"{phone}.session"
        self.client = TelegramClient(self.session_file, self.api_id, self.api_hash)

    def connect(self):
        if os.path.exists(self.session_file):
            self.client.start()
        else:
            self.client.connect()
            if not self.client.is_user_authorized():
                self.client.send_code_request(self.phone)
                self.client.sign_in(self.phone, input('Digite o código:'))

    def get_my_groups(self):
        groups = []

        chats = self.client(GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=200,
            hash=0))

        for chat in chats.chats:
            try:
                if chat.megagroup == True:
                    groups.append(chat)
            except:
                continue

        print("Escolha o grupo de onde deseja extrair os membros:")
        for i, group in enumerate(groups):
            print(f"{i} - {group.title}")

        escolha = int(input("Digite o número correspondente ao grupo: "))
        grupo_origem = groups[escolha]

        return grupo_origem

    def choose_target_group(self):
        groups = []

        chats = self.client(GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=200,
            hash=0))

        for chat in chats.chats:
            try:
                if chat.megagroup == True:
                    groups.append(chat)
            except:
                continue

        print("Escolha o grupo para adicionar os membros:")
        for i, group in enumerate(groups):
            print(f"{i} - {group.title}")

        escolha = int(input("Digite o número correspondente ao grupo: "))
        grupo_alvo = groups[escolha]

        return grupo_alvo

    def get_members_of_group(self, target_group):
        all_participants = self.client.get_participants(
            target_group, aggressive=True)
        return all_participants

    def add_member_to_group(self, user, target_group):
        target_group_entity = InputPeerChannel(
            target_group.id, target_group.access_hash)

        try:
            print(f"Adicionando usuário {user.id} ao grupo...")
            user_to_add = InputPeerUser(user.id, user.access_hash)

            self.client(InviteToChannelRequest(
                target_group_entity, [user_to_add]))
            time.sleep(10)
            print("Usuário adicionado com sucesso!")
            return True

        except PeerFloodError:
            print("Erro de Flood. Dormindo por 1 hora.")
            time.sleep(3600)
            return False

        except UserPrivacyRestrictedError:
            print("Usuário não permite ser adicionado no grupo")
            time.sleep(20)
            return False

        except Exception as e:
            print(f"Erro ao adicionar usuário: {str(e)}")
            return False

# Exemplo de uso
if __name__ == "__main__":
    api_id = int(input('API ID: '))
    api_hash = input('API HASH: ')
    phone = input('TELEFONE: ')

    bot = TelegramBot(api_id, api_hash, phone)
    bot.connect()
    
    source_group = bot.get_my_groups()
    group_members = bot.get_members_of_group(source_group)

    target_group = bot.choose_target_group()
    
    for member in group_members:
        bot.add_member_to_group(member, target_group)