from cli.core.config import Config
from cli.command.main import noj


def main():
    Config.load()
    noj()


if __name__ == '__main__':
    main()
