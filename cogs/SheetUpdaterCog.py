import discord
import gspread
import requests
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials

SPREADSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/1IRzkAwYgIONjnoZU7WKvSHDMrvk8M23hJXS9Fc-CNLo/edit?usp=sharing"
)

SHEET_TAB_NAME = "shards"

ITEMS_TO_UPDATE = {
    "SHARD_MOCHIBEAR": ("B1", "buyPrice"),
    "SHARD_BAMBULEAF": ("B2", "buyPrice"),
    "SHARD_GLACITE_WALKER": ("B3", "buyPrice"),
    "SHARD_PANDARAI": ("B4", "buyPrice"),
    "SHARD_BAMBLOOM": ("B5", "buyPrice"),
    "SHARD_CHILL": ("B14", "sellPrice"),
    "SHARD_PEST": ("B15", "sellPrice"),
    "SHARD_PRAYING_MANTIS": ("B16", "buyPrice"),
    "SHARD_MINER_ZOMBIE": ("B17", "sellPrice"),
    "SHARD_INVISIBUG": ("B18", "sellPrice"),
    "SHARD_TERMITE": ("B19", "sellPrice"),
    "SHARD_CROPEETLE": ("B20", "sellPrice"),
}

class SheetUpdaterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_bazaar_prices(self):
            url = "https://api.hypixel.net/v2/skyblock/bazaar"
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                raise RuntimeError(f"{e}")

            if not data.get("success"):
                raise RuntimeError("API Response Failure")
                
            return data.get("products", {})

    def update_google_sheet(self, bazaar_data):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "credentials.json", scope
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_url(SPREADSHEET_URL).worksheet(SHEET_TAB_NAME)
        except Exception as e:
            raise RuntimeError(f"{e}")
        
        cell_updates = []
        missing_items = []

        for item_id, (cell, api_key) in ITEMS_TO_UPDATE.items():
            if item_id in bazaar_data:
                product_status = bazaar_data[item_id].get("quick_status", {})

                price = round(product_status.get(api_key, 0), 2)
                
                cell_updates.append({"range": cell, "values": [[price]]})
            else:
                missing_items.append(item_id)

        if missing_items:
            raise ValueError(f"Items were not found: `{', '.join(missing_items)}`")

        if cell_updates:
            try:
                sheet.batch_update(cell_updates, value_input_option='USER_ENTERED')
            except Exception as e:
                raise RuntimeError(f"{e}")
    
    @commands.command(name="update")
    async def update(self, ctx):
        try:
            bazaar_data = self.get_bazaar_prices()
            self.update_google_sheet(bazaar_data)
            embed = discord.Embed(title="Sheet Updated", color=discord.Color.green())
            await ctx.reply(embed=embed)
        except (RuntimeError, ValueError) as e:
            embed = discord.Embed(title="Error", description=f"{e}", color=discord.Color.red())
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Error", description=f"{e}", color=discord.Color.red())
            await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(SheetUpdaterCog(bot))