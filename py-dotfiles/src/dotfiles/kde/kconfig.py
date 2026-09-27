from dotfiles import process


async def kwriteconfig6(
    *,
    delete=False,
    file=None,
    groups=None,
    key=None,
    notify=False,
    value_type=None,
    value=None,
):
    args = ["kwriteconfig6"]
    if file is not None:
        args.extend(("--file", file))
    if groups is not None:
        if isinstance(groups, str):
            groups = [groups]
        for group in groups:
            args.extend(("--group", group))
    if key is not None:
        args.extend(("--key", key))
    if value_type is not None:
        args.extend(("--type", value_type))
    if delete:
        args.append("--delete")
    if notify:
        args.append("--notify")
    if not delete and value:
        args.append(value)
    if value is not None:
        args.append(value)
    await process.run(*args)


async def kreadconfig6(*, file=None, groups=None, key=None, default=None):
    args = ["kreadconfig6"]
    if file is not None:
        args.extend(("--file", file))
    if groups is not None:
        if isinstance(groups, str):
            groups = [groups]
        for group in groups:
            args.extend(("--group", group))
    if key is not None:
        args.extend(("--key", key))
    if default is not None:
        args.extend(("--default", default))
    result = await process.run(*args, stdout=process.PIPE, stderr=process.PIPE)
    return result.stdout.decode().strip()
