# https://github.com/Reecepbcups/minecraft-panel/blob/main/src/utils/notifications.py
# https://github.com/Reecepbcups/validator-stats-notifs/blob/main/src/utils/notifications.py

from discord_webhook import DiscordWebhook, DiscordEmbed

def discord_notification(webook_url="", title="", description="", color="ffffff", values={}, thumbnail="", image="", footerText=""):
    webhook = DiscordWebhook(url=webook_url)
    
    embed = DiscordEmbed(
        title=title, 
        description=description, 
        color=color
    )   
    # # set thumbnail
    if len(thumbnail) > 0:
        embed.set_thumbnail(url=thumbnail)
    if len(image) > 0:
        embed.set_image(url=image)
    
    embed.set_footer(text=footerText)
    # embed.set_timestamp()

    if len(values.items()) > 0:
        for k, v in values.items():
            embed.add_embed_field(name=k, value=v[0], inline=v[1])

    webhook.add_embed(embed)
    response = webhook.execute()


# graph notification
def discord_graph_notification(webhook="", title="", description="", color="ffffff", values={}, graph_image_links=[], thumbnail="", footer=""):
    webhook = DiscordWebhook(url=webhook)
    
    embed = DiscordEmbed(
        title=title, 
        description=description, 
        color=color,        
    )   

    for idx, image_link in enumerate(graph_image_links):
        if idx == 0:
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text=footer)
            if len(values.items()) > 0:
                for k, v in values.items():
                    embed.add_embed_field(name=k, value=v[0], inline=v[1])
            embed.set_image(url=image_link)        
            webhook.add_embed(embed)
        else:
            # graphs get their own blank embeds (no title / desk)
            embed = DiscordEmbed(
                color=color,
            )   
            embed.set_image(url=image_link)
            webhook.add_embed(embed)

    response = webhook.execute() 

if __name__ == "__main__":
    discord_notification(
        "webhookurl",
        "Oni Validator Stats",
        "desc",
        "D04045",
        {"test": ["value", False]},
        "https://pbs.twimg.com/profile_images/1522666990170746881/OHpOzKDD_400x400.jpg",
        "The Oni Protectorate ⚛️\nValidator for the Cosmos. Friend to the Cosmonaut."
    )