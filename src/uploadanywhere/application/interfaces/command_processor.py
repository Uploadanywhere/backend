import typing as t


class CommandProcessor[CommandT, ResultT](t.Protocol):
    async def process(self, command: CommandT) -> ResultT: ...
