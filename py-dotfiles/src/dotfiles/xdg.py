from dotfiles import process


async def update_desktop_database():
    await process.run("update-desktop-database")
