from dotfiles import process

try:
    import pyalpm
except ImportError as e:
    raise ImportError(
        "pyalpm not found; requires Arch Linux and the arch-linux extra"
    ) from e


def local_packages():
    handle = pyalpm.Handle(".", "/var/lib/pacman")
    return handle.get_localdb().pkgcache


def is_explicit(package):
    return package.reason == pyalpm.PKG_REASON_EXPLICIT


class Pacman:
    @staticmethod
    async def install(packages, asdeps=False):
        args = ["sudo", "pacman", "-S", "--needed", "--overwrite", "*"]
        if asdeps:
            args.append("--asdeps")
        args.extend(["--", *packages])
        await process.run(*args)

    @staticmethod
    async def set_reason(packages, explicit=False, asdeps=False):
        if explicit and asdeps:
            raise ValueError("Cannot set both explicit and asdeps")
        if not explicit and not asdeps:
            raise ValueError("Must set either explicit or asdeps")
        args = ["sudo", "pacman", "-D"]
        if explicit:
            args.append("--asexplicit")
        if asdeps:
            args.append("--asdeps")
        args.extend(["--", *packages])
        await process.run(*args)
