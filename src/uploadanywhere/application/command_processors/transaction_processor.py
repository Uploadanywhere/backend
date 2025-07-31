from uploadanywhere.application.interfaces.command_processor import CommandProcessor
from uploadanywhere.application.interfaces.uow import AsyncUoW


class TransactionProcessor[T, E](CommandProcessor[T, E]):
    def __init__(self, uow: AsyncUoW, processor: CommandProcessor[T, E]) -> None:
        self._uow = uow
        self._processor = processor

    async def process(self, command: T) -> E:
        result = await self._processor.process(command)
        await self._uow.commit()
        return result
