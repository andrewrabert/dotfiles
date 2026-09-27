from dotfiles import process


class UserGroup:
    @staticmethod
    async def add_to_group(user, group):
        print(f"Adding user {user} to group {group}")
        await process.run(
            "sudo", "gpasswd", "-a", user, group, stdout=process.DEVNULL
        )
