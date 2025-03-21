import struct
from typing import Optional, List
from telethon.tl import TLObject, TLRequest
from telethon.tl.types import TypeStarGift, TypeInputUser, TypeUser, TypeTextWithEntities


class UserStarGift(TLObject):
    """Represents a single gift received by a user."""
    CONSTRUCTOR_ID = 0xeea49a6e
    SUBCLASS_OF_ID = None

    def __init__(self, gift: 'TypeStarGift', date: int, name_hidden: Optional[bool] = None,
                 unsaved: Optional[bool] = None, from_id: Optional[int] = None,
                 message: Optional['TypeTextWithEntities'] = None, msg_id: Optional[int] = None,
                 convert_stars: Optional[int] = None):
        self.gift = gift
        self.date = date
        self.name_hidden = name_hidden
        self.unsaved = unsaved
        self.from_id = from_id
        self.message = message
        self.msg_id = msg_id
        self.convert_stars = convert_stars

    def to_dict(self):
        return {
            '_': 'UserStarGift',
            'gift': self.gift.to_dict() if isinstance(self.gift, TLObject) else self.gift,
            'date': self.date,
            'name_hidden': self.name_hidden,
            'unsaved': self.unsaved,
            'from_id': self.from_id,
            'message': self.message.to_dict() if isinstance(self.message, TLObject) else self.message,
            'msg_id': self.msg_id,
            'convert_stars': self.convert_stars
        }

    def _bytes(self):
        flags = 0
        if self.name_hidden:
            flags |= 1
        if self.from_id is not None:
            flags |= 2
        if self.message is not None:
            flags |= 4
        if self.msg_id is not None:
            flags |= 8
        if self.convert_stars is not None:
            flags |= 16
        if self.unsaved:
            flags |= 32
        return b''.join((
            b'\x6e\x9a\xa4\xee',
            struct.pack('<I', flags),
            struct.pack('<q', self.from_id) if self.from_id is not None else b'',
            struct.pack('<i', self.date),
            self.gift._bytes(),
            self.message._bytes() if self.message is not None else b'',
            struct.pack('<i', self.msg_id) if self.msg_id is not None else b'',
            struct.pack('<q', self.convert_stars) if self.convert_stars is not None else b'',
        ))

    @classmethod
    def from_reader(cls, reader):
        flags = reader.read_int()
        name_hidden = bool(flags & 1)
        from_id = reader.read_long() if flags & 2 else None
        date = reader.read_int()
        gift = reader.tgread_object()
        message = reader.tgread_object() if flags & 4 else None
        msg_id = reader.read_int() if flags & 8 else None
        convert_stars = reader.read_long() if flags & 16 else None
        unsaved = bool(flags & 32)
        return cls(gift=gift, date=date, name_hidden=name_hidden, unsaved=unsaved,
                   from_id=from_id, message=message, msg_id=msg_id, convert_stars=convert_stars)


class UserStarGifts(TLObject):
    """Represents a collection of user gifts."""
    CONSTRUCTOR_ID = 0x6b65b517
    SUBCLASS_OF_ID = None

    def __init__(self, count: int, gifts: List['UserStarGift'], users: List['TypeUser'],
                 next_offset: Optional[str] = None):
        self.count = count
        self.gifts = gifts
        self.next_offset = next_offset
        self.users = users

    def to_dict(self):
        return {
            '_': 'UserStarGifts',
            'count': self.count,
            'gifts': [x.to_dict() if isinstance(x, TLObject) else x for x in self.gifts],
            'next_offset': self.next_offset,
            'users': [x.to_dict() if isinstance(x, TLObject) else x for x in self.users]
        }

    def _bytes(self):
        flags = 0 if self.next_offset is None else 1
        return b''.join((
            b'\x17\xb5\x65\x6b',
            struct.pack('<I', flags),
            struct.pack('<i', self.count),
            b'\x15\xc4\xb5\x1c', struct.pack('<i', len(self.gifts)),
            b''.join(x._bytes() for x in self.gifts),
            self.serialize_bytes(self.next_offset.encode('utf-8')) if self.next_offset else b'',
            b'\x15\xc4\xb5\x1c', struct.pack('<i', len(self.users)),
            b''.join(x._bytes() for x in self.users),
        ))

    @classmethod
    def from_reader(cls, reader):
        flags = reader.read_int()
        count = reader.read_int()
        reader.read_int()  # Vector header
        gifts = [reader.tgread_object() for _ in range(reader.read_int())]
        next_offset = reader.tgread_string() if flags & 1 else None
        reader.read_int()  # Vector header
        users = [reader.tgread_object() for _ in range(reader.read_int())]
        return cls(count=count, gifts=gifts, next_offset=next_offset, users=users)


class GetUserStarGifts(TLRequest):
    """Request to fetch user gifts."""
    CONSTRUCTOR_ID = 0x5e72c7e1
    SUBCLASS_OF_ID = 0x6b65b517

    def __init__(self, user_id: 'TypeInputUser', offset: str, limit: int):
        self.user_id = user_id
        self.offset = offset
        self.limit = limit

    def to_dict(self):
        return {
            '_': 'GetUserStarGifts',
            'user_id': self.user_id.to_dict() if isinstance(self.user_id, TLObject) else self.user_id,
            'offset': self.offset,
            'limit': self.limit
        }

    def _bytes(self):
        return b''.join((
            b'\xe1\xc7\x72\x5e',
            self.user_id._bytes(),
            self.serialize_bytes(self.offset.encode('utf-8')),
            struct.pack('<i', self.limit),
        ))

    @classmethod
    def from_reader(cls, reader):
        user_id = reader.tgread_object()
        offset = reader.tgread_string()
        limit = reader.read_int()
        return cls(user_id=user_id, offset=offset, limit=limit)
