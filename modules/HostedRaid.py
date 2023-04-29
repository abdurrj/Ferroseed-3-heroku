import discord

from BotImports import *


class HostedRaid:
    def __init__(
            self,
            raidStartMessage:discord.Message,
            raidHost:discord.User,
            maxUsers:int,
            isLocked:bool,
            channelName:str,
            channelDescription:str=None,
            raidChannel:discord.TextChannel=None,
            raidJoinMessage:discord.Message=None
    ):
        self.raidStartMessage = raidStartMessage
        self.raidHost = raidHost
        self.maxUsers = maxUsers
        self.isLocked = isLocked
        self.channelName = channelName
        self.channelDescription = channelDescription
        self.raidChannel = raidChannel
        self.raidJoinMessage = raidJoinMessage
        self.currentUsers = 0
        self.linkCode = None
        self.participants = []
        self.pinnedMessages = [] # Or maybe echo? to repeat messages... pinned should just pin to raid


    def isFull(self):
        return int(self.currentUsers) >= int(self.maxUsers)

    def switchRaidLockStatus(self):
        if self.isLocked:
            self.isLocked = False
        else:
            self.isLocked = True
        return self.isLocked
