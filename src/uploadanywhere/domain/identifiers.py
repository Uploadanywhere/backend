import typing as t

from uuid6 import UUID

SessionId = t.NewType("SessionId", UUID)
UserId = t.NewType("UserId", UUID)
WorkspaceId = t.NewType("WorkspaceId", UUID)
SocialAccountId = t.NewType("SocialAccountId", UUID)
PostId = t.NewType("PostId", UUID)
