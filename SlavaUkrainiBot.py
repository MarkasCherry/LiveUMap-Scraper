import discord
import os
from discord.ext import tasks
from dotenv import load_dotenv
import random
from Database import Database

def main():
    load_dotenv()

    DEBUG = eval(os.environ.get("DEBUG"))

    client = discord.Client()

    @client.event
    async def on_ready():
        post_event.start()
        print('BOT {0.user} is ready.'.format(client))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if "SLAVA UKRAINI" in message.content.upper():
            await message.channel.send('**GEROYAM SLAVA!**')

        if "PUTIN" in message.content.upper():
            await message.channel.send('**HUILO**')


        if "WARSHIP" in message.content.upper():
            await message.channel.send('**GO FUCK YOURSELF!**')

    @tasks.loop(minutes=1)
    async def post_event():
        try:
            db = Database(
                os.environ.get("DB_HOST"),
                os.environ.get("DB_USER"),
                os.environ.get("DB_PASSWORD"),
                os.environ.get("DB_DATABASE")
            )

        except Exception as e:
            if DEBUG:
                print('[DEBUG] ' + e)

            print('[ERROR] FAILED CONNECTING TO DATABASE')

        unposted_events = db.get_unposted_events()

        if unposted_events is not False:
            for event in unposted_events:
                title = event[1]
                source = event[2]
                image = event[3]
                date = event[4]

                embed = discord.Embed(title=title,
                                      url=source,
                                      description=str(date) + "\n:flag_ua:",
                                      color=random.choice([0xFFD500, 0x005BBB]))

                if image is not None:
                    embed.set_image(url=image)

                await client.get_channel(945588302562623519).send(embed=embed)

            db.mark_as_posted(unposted_events)


    client.run('PROVIDE TOKEN')


if __name__ == "__main__":
    main()
