**Ferroseed bot 3.0**
First, a special thank you to my friends on the server Ferroseed bot was made for.
I entered this project with no knowledge of programming. They've helped me with problems I have
encountered and motivated me to learn more so I can make a better bot for them.

It's main feature is the seed checking feature, which I have had nothing to do with. See credits.

Additional features have been added, such as reaction roles, polls
and a giveaway that picks user(s) from reactions on your giveaway message

A couple of pokemon related commands, like dex and sprite lookup, ability to create raid channels, friendcode lookup
and getting links to different raid dens.

Some extra commands for fun.

There are a lot of things commented out in the code. Either thing I'm working on, or just comments left for myself.
Just ignore all that.

**Prerequisites:**
Please use by installing python3. 

You must have nextcord installed. Follow instructions [here](https://github.com/nextcord/nextcord)

Then pip install all modules used by the bot:
- pandas
- xlrd
- numpy
- emoji


If you want to use seed finder, please follow instructions [here](https://gitlab.com/fishguy6564/lanturn-bot-public-source-code)


**How to Run**
Ferroseed can work on multiple servers. On guild join it adds a standard prefix `fb!`, which can be changed by the command `change_prefix`.
the fc module needs a fc.json file in the data folder. It's left out as it contains fc info for different devices.
Create a file called `fc.json` and add `{}`in it. rest works on its own.

If you just want the discord bot:
Download everything except RaidCommands.py and the seed folder.

If you are interested in running the sys-bot and seed checking, Please follow the repository [here](https://gitlab.com/fishguy6564/lanturn-bot-public-source-code)


**Questions?**
For questions regarding the sys-bot and seed checking, Please follow the repository [here](https://gitlab.com/fishguy6564/lanturn-bot-public-source-code)

For questions directed to Ferroseed bot and it's features, find me on discord: Abdur#0846


**Known Bugs**
- The current `poll` command does not work with flags and numbers. 
  Using flags in poll results in the bot reacting with letters instead of flags.
  I have an updated code that works, but it's left out because server found this bug hilarous.



**Credit:**

Base of the bot is designed by fishguy6564, you can read more about it [here](https://gitlab.com/fishguy6564/lanturn-bot-public-source-code)
Used algorithms and documentation from various Pokemon hackers
such as Admiral-Fish and zaksabeast

olliz0r for the sys-botbase sysmodule

Files in the data folder are from [Alcremie-B](https://github.com/RaphGG/den-bot)
