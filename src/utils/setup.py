
# async def inspect_cog(cog_name: str):
#     cog = bot.get_cog(cog_name)
#     commands = cog.get_app_commands()
#     logger.info([c.name for c in commands])

# async def load_cogs():
#     """
#     Dynamically loads all cogs from the `cogs` folder.
#     """
#     for filename in os.listdir("src/cogs"):
#         if filename.endswith(".py"):
#             try:
#                 await bot.load_extension(f"cogs.{filename[:-3]}")
#                 logger.info(f"Loaded extension: {filename}")
#             except Exception as e:
#                 logger.error(f"Failed to load extension {filename}: {e}")

# async def unload_cogs():
#     """
#     Dynamically loads all cogs from the `cogs` folder.
#     """
#     for filename in os.listdir("src/cogs"):
#         if filename.endswith(".py"):
#             try:
#                 await bot.unload_extension(f"cogs.{filename[:-3]}")
#                 logger.info(f"Unloaded extension: {filename}")
#             except Exception as e:
#                 logger.error(f"Failed to unload extension {filename}: {e}")

# async def remove_cogs():
#     for filename in os.listdir("src/cogs"):
#         if filename.endswith(".py"):
#             try:
#                 await bot.remove_cog(f"cogs.{filename[:-3]}")
#                 logger.info(f"Removed extension: {filename}")
#             except Exception as e:
#                 logger.error(f"Failed to remove extension {filename}: {e}")

# async def clear_commands():
#     bot.tree.clear_commands(guild=MY_GUILD)
#     bot.recursively_remove_all_commands()
#     await bot.tree.sync(guild=MY_GUILD)

# async def sync_tree():
#     bot.tree.copy_global_to(guild=MY_GUILD)
#     await bot.tree.sync(guild=MY_GUILD)