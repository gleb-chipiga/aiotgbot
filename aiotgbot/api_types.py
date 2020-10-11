from typing import (Any, AsyncIterator, BinaryIO, Dict, Generator, Iterable,
                    List, Optional, Set, Tuple, Type, TypeVar, Union, cast,
                    get_args, get_origin, get_type_hints)

import attr


class DataMappingError(BaseException):
    pass


@attr.s(slots=True, frozen=True, auto_attribs=True)
class StreamFile:
    content: AsyncIterator[bytes]
    filename: str
    content_type: Optional[str] = None


def _is_tuple(_type: Any) -> bool:
    return get_origin(_type) is tuple


def _is_list(_type: Any) -> bool:
    return get_origin(_type) is list


def _is_union(_type: Any) -> bool:
    return get_origin(_type) is Union


def _is_optional(_type: Any) -> bool:
    return _type is Any or (_is_union(_type) and type(None) in get_args(_type))


def _is_attr_union(_type: Any) -> bool:
    return _is_union(_type) and all(attr.has(arg_type) or arg_type is _NoneType
                                    for arg_type in get_args(_type))


_NoneType: Type[None] = type(None)
_FieldType = Union[int, str, bool, float, Tuple, List, 'BaseTelegram']
_TelegramType = TypeVar('_TelegramType', bound='BaseTelegram')
_HintsGenerator = Generator[Tuple[str, str, Any], None, None]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class BaseTelegram:

    def to_dict(self) -> Dict[str, Any]:
        _dict: Dict[str, Any] = {}
        for _attr in attr.fields(type(self)):
            value = getattr(self, _attr.name)
            key = _attr.name.rstrip('_')
            if isinstance(value, BaseTelegram):
                _dict[key] = value.to_dict()
            elif isinstance(value, (tuple, list)):
                _dict[key] = BaseTelegram._to_list(value)
            elif isinstance(value, (int, str, bool, float)):
                _dict[key] = value
            elif value is None:
                continue
            else:
                raise TypeError(f'"{value}" has unsupported type')

        return _dict

    @staticmethod
    def _to_list(value: Iterable) -> List[Any]:
        _list: List[Any] = []
        for item in value:
            if isinstance(item, (int, str, bool, float)):
                _list.append(item)
            elif isinstance(item, (tuple, list)):
                _list.append(BaseTelegram._to_list(item))
            elif isinstance(item, BaseTelegram):
                _list.append(item.to_dict())
            else:
                raise TypeError(f'"{item}" has unsupported type')

        return _list

    @classmethod
    def get_type_hints(cls: Type[_TelegramType]) -> _HintsGenerator:
        return ((field.rstrip('_'), field, _type)
                for field, _type in get_type_hints(cls).items())

    @classmethod
    def from_dict(cls: Type[_TelegramType],
                  data: Dict[str, Any]) -> _TelegramType:
        return BaseTelegram.handle_object(cls, data)

    @staticmethod
    def handle_object(cls: Type[_TelegramType],
                      data: Dict[str, Any]) -> _TelegramType:
        required = set(field for field, _, _type in cls.get_type_hints()
                       if not _is_optional(_type))
        filled = set(key for key, value in data.items() if value is not None)
        if not required <= filled:
            keys = ', '.join(required - filled)
            raise DataMappingError(f'Data without required keys: {keys}')
        params = {}
        for key, field, type_ in cls.get_type_hints():
            params[field] = BaseTelegram.handle_field(type_, data.get(key))

        return cast(Any, cls)(**params)

    @staticmethod
    def handle_field(_type: Any, value: Any) -> Optional[_FieldType]:
        if _type in (int, str, bool, float) and isinstance(value, _type):
            return value
        elif _type in (int, str, bool, float):
            message = f'"{value}" is not instance of type "{_type.__name__}"'
            raise DataMappingError(message)
        elif _type is _NoneType and value is None:
            return None
        elif _type is _NoneType:
            raise DataMappingError(f'"{value}" is not None')
        elif _type is Any:
            return value
        elif _is_tuple(_type) and isinstance(value, list):
            return tuple(BaseTelegram.handle_field(get_args(_type)[0], item)
                         for item in value)
        elif _is_list(_type) and isinstance(value, list):
            return [BaseTelegram.handle_field(get_args(_type)[0], item)
                    for item in value]
        elif _is_list(_type) or _is_tuple(_type):
            raise DataMappingError(f'Data "{value}" is not list')
        elif _is_optional(_type) and value is None:
            return None
        elif _is_optional(_type) and len(get_args(_type)) == 2:
            return BaseTelegram.handle_field(get_args(_type)[0], value)
        elif _is_attr_union(_type) and isinstance(value, dict):
            types: List[Tuple[int, Any]] = []
            for arg_type in get_args(_type):
                fields: Set[str] = set(key.rstrip('_') for key
                                       in get_type_hints(arg_type).keys())
                data_keys: Set[str] = set(value.keys())
                if not data_keys <= fields:
                    continue
                types.append((len(fields & data_keys), arg_type))
            if len(types) == 0:
                arg_types = ', '.join(t.__name__ for t in get_args(_type))
                message = f'Data "{value}" not match any of "{arg_types}"'
                raise DataMappingError(message)
            types = sorted(types, key=lambda t: t[0], reverse=True)
            return BaseTelegram.handle_field(types[0][1], value)
        elif attr.has(_type) and isinstance(value, dict):
            return BaseTelegram.handle_object(_type, value)
        else:
            message = f'Data "{value}" not match field type "{_type}"'
            raise DataMappingError(message)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ResponseParameters(BaseTelegram):
    migrate_to_chat_id: Optional[int]
    retry_after: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class APIResponse(BaseTelegram):
    ok: bool
    result: Any
    error_code: Optional[int]
    description: Optional[str]
    parameters: Optional[ResponseParameters]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Update(BaseTelegram):
    update_id: int
    message: Optional['Message']
    edited_message: Optional['Message']
    channel_post: Optional['Message']
    edited_channel_post: Optional['Message']
    inline_query: Optional['InlineQuery']
    chosen_inline_result: Optional['ChosenInlineResult']
    callback_query: Optional['CallbackQuery']
    shipping_query: Optional['ShippingQuery']
    pre_checkout_query: Optional['PreCheckoutQuery']
    poll: Optional['Poll']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class WebhookInfo(BaseTelegram):
    url: Optional[str]
    has_custom_certificate: Optional[bool]
    pending_update_count: Optional[int]
    last_error_date: Optional[int]
    last_error_message: Optional[str]
    max_connections: Optional[int]
    allowed_updates: Tuple[str, ...]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class User(BaseTelegram):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    language_code: Optional[str]
    sticker_set_name: Optional[str]
    can_set_sticker_set: Optional[bool]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Chat(BaseTelegram):
    id: int
    type: str
    title: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    photo: Optional['ChatPhoto']
    description: Optional[str]
    invite_link: Optional[str]
    pinned_message: Optional['Message']
    permissions: Optional['ChatPermissions'] = None
    slow_mode_delay: Optional[int] = None


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Message(BaseTelegram):
    message_id: int
    from_: Optional[User]
    date: int
    chat: Chat
    forward_from: Optional[User]
    forward_from_chat: Optional[Chat]
    forward_from_message_id: Optional[int]
    forward_signature: Optional[str]
    forward_sender_name: Optional[str]
    forward_date: Optional[int]
    reply_to_message: Optional['Message']
    edit_date: Optional[int]
    media_group_id: Optional[str]
    author_signature: Optional[str]
    text: Optional[str]
    entities: Optional[Tuple['MessageEntity', ...]]
    caption_entities: Optional[Tuple['MessageEntity', ...]]
    audio: Optional['Audio']
    document: Optional['Document']
    animation: Optional['Animation']
    game: Optional['Game']
    photo: Optional[Tuple['PhotoSize', ...]]
    sticker: Optional['Sticker']
    video: Optional['Video']
    voice: Optional['Voice']
    video_note: Optional['VideoNote']
    caption: Optional[str]
    contact: Optional['Contact']
    location: Optional['Location']
    venue: Optional['Venue']
    poll: Optional['Poll']
    new_chat_members: Optional[Tuple[User, ...]]
    left_chat_member: Optional[User]
    new_chat_title: Optional[str]
    new_chat_photo: Optional[Tuple['PhotoSize', ...]]
    delete_chat_photo: Optional[bool]
    group_chat_created: Optional[bool]
    supergroup_chat_created: Optional[bool]
    channel_chat_created: Optional[bool]
    migrate_to_chat_id: Optional[int]
    migrate_from_chat_id: Optional[int]
    pinned_message: Optional['Message']
    invoice: Optional['Invoice']
    successful_payment: Optional['SuccessfulPayment']
    connected_website: Optional[str]
    passport_data: Optional['PassportData']
    reply_markup: Optional['InlineKeyboardMarkup']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class MessageEntity(BaseTelegram):
    type: str
    offset: int
    length: int
    url: Optional[str]
    user: Optional[User]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PhotoSize(BaseTelegram):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: int


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Audio(BaseTelegram):
    file_id: str
    file_unique_id: str
    duration: int
    performer: Optional[str]
    title: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]
    thumb: Optional[PhotoSize]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Document(BaseTelegram):
    file_id: str
    file_unique_id: str
    thumb: Optional[PhotoSize]
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Video(BaseTelegram):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: Optional[PhotoSize]
    mime_type: Optional[str]
    file_size: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Animation(BaseTelegram):
    file_id: str
    file_unique_id: str
    thumb: Optional[PhotoSize]
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Voice(BaseTelegram):
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: Optional[str]
    file_size: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class VideoNote(BaseTelegram):
    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumb: Optional[PhotoSize]
    file_size: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Contact(BaseTelegram):
    phone_number: str
    first_name: str
    last_name: Optional[str]
    user_id: Optional[int]
    vcard: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Location(BaseTelegram):
    longitude: float
    latitude: float


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Venue(BaseTelegram):
    location: Location
    title: str
    address: str
    foursquare_id: Optional[str]
    foursquare_type: Optional[str]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PollOption(BaseTelegram):
    text: str
    voter_count: int


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Poll(BaseTelegram):
    id: str
    question: str
    options: Tuple[PollOption, ...]
    is_closed: bool


@attr.s(slots=True, frozen=True, auto_attribs=True)
class UserProfilePhotos(BaseTelegram):
    total_count: int
    photos: Tuple[Tuple[PhotoSize, ...], ...]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class File(BaseTelegram):
    file_id: str
    file_unique_id: str
    file_size: Optional[int]
    file_path: Optional[str]


ReplyMarkup = Union['InlineKeyboardMarkup',
                    'ReplyKeyboardMarkup',
                    'ReplyKeyboardRemove',
                    'ForceReply']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ReplyKeyboardMarkup(BaseTelegram):
    keyboard: List[List['KeyboardButton']]
    resize_keyboard: Optional[bool] = None
    one_time_keyboard: Optional[bool] = None
    selective: Optional[bool] = None


@attr.s(slots=True, frozen=True, auto_attribs=True)
class KeyboardButton(BaseTelegram):
    text: str
    request_contact: Optional[bool] = None
    request_location: Optional[bool] = None


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ReplyKeyboardRemove(BaseTelegram):
    remove_keyboard: bool
    selective: Optional[bool] = None


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineKeyboardMarkup(BaseTelegram):
    inline_keyboard: List[List['InlineKeyboardButton']]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineKeyboardButton(BaseTelegram):
    text: str
    url: Optional[str] = None
    login_url: Optional['LoginUrl'] = None
    callback_data: Optional[str] = None
    switch_inline_query: Optional[str] = None
    switch_inline_query_current_chat: Optional[str] = None
    callback_game: Optional['CallbackGame'] = None
    pay: Optional[bool] = None


@attr.s(slots=True, frozen=True, auto_attribs=True)
class LoginUrl(BaseTelegram):
    url: str
    forward_text: Optional[str]
    bot_username: Optional[str]
    request_write_access: Optional[bool] = None


@attr.s(slots=True, frozen=True, auto_attribs=True)
class CallbackQuery(BaseTelegram):
    id: str
    from_: User
    message: Optional[Message]
    inline_message_id: Optional[str]
    chat_instance: str
    data: Optional[str]
    game_short_name: Optional[str]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ForceReply(BaseTelegram):
    force_reply: bool
    selective: Optional[bool]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ChatPhoto(BaseTelegram):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_file_unique_id: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ChatMember(BaseTelegram):
    user: User
    status: str
    custom_title: str
    until_date: Optional[int]
    can_be_edited: Optional[bool]
    can_change_info: Optional[bool]
    can_post_messages: Optional[bool]
    can_edit_messages: Optional[bool]
    can_delete_messages: Optional[bool]
    can_invite_users: Optional[bool]
    can_restrict_members: Optional[bool]
    can_pin_messages: Optional[bool]
    can_promote_members: Optional[bool]
    is_member: Optional[bool]
    can_send_messages: Optional[bool]
    can_send_media_messages: Optional[bool]
    can_send_other_messages: Optional[bool]
    can_add_web_page_previews: Optional[bool]
    can_send_polls: Optional[bool]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ChatPermissions(BaseTelegram):
    can_send_messages: Optional[bool] = None
    can_send_media_messages: Optional[bool] = None
    can_send_polls: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_pin_messages: Optional[bool] = None


InputMedia = Union['InputMediaAnimation',
                   'InputMediaDocument',
                   'InputMediaAudio',
                   'InputMediaPhoto',
                   'InputMediaVideo']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InputMediaPhoto(BaseTelegram):
    type: str
    media: str
    caption: Optional[str]
    parse_mode: Optional[str]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InputMediaVideo(BaseTelegram):
    type: str
    media: str
    thumb: Optional[str]
    caption: Optional[str]
    parse_mode: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[int]
    supports_streaming: Optional[bool]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InputMediaAnimation(BaseTelegram):
    type: str
    media: str
    thumb: Optional[str]
    caption: Optional[str]
    parse_mode: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InputMediaAudio(BaseTelegram):
    type: str
    media: str
    thumb: Optional[str]
    caption: Optional[str]
    parse_mode: Optional[str]
    duration: Optional[int]
    performer: Optional[str]
    title: Optional[str]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InputMediaDocument(BaseTelegram):
    type: str
    media: str
    thumb: Optional[str]
    caption: Optional[str]
    parse_mode: Optional[str]


InputFile = Union[BinaryIO, StreamFile]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Sticker(BaseTelegram):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    is_animated: bool
    thumb: Optional[PhotoSize]
    emoji: Optional[str]
    set_name: Optional[str]
    mask_position: Optional['MaskPosition']
    file_size: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class StickerSet(BaseTelegram):
    name: str
    title: str
    is_animated: bool
    contains_masks: bool
    stickers: Tuple[Sticker, ...]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class MaskPosition(BaseTelegram):
    point: str
    x_shift: float
    y_shift: float
    scale: float


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQuery(BaseTelegram):
    id: str
    from_: User
    location: Optional[Location]
    query: str
    offset: str


InlineQueryResult = Union['InlineQueryResultCachedAudio',
                          'InlineQueryResultCachedDocument',
                          'InlineQueryResultCachedGif',
                          'InlineQueryResultCachedMpeg4Gif',
                          'InlineQueryResultCachedPhoto',
                          'InlineQueryResultCachedSticker',
                          'InlineQueryResultCachedVideo',
                          'InlineQueryResultCachedVoice',
                          'InlineQueryResultArticle',
                          'InlineQueryResultAudio',
                          'InlineQueryResultContact',
                          'InlineQueryResultGame',
                          'InlineQueryResultDocument',
                          'InlineQueryResultGif',
                          'InlineQueryResultLocation',
                          'InlineQueryResultMpeg4Gif',
                          'InlineQueryResultPhoto',
                          'InlineQueryResultVenue',
                          'InlineQueryResultVideo',
                          'InlineQueryResultVoice']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultArticle(BaseTelegram):
    type: str
    id: str
    title: str
    input_message_content: 'InputMessageContent'
    reply_markup: Optional[InlineKeyboardMarkup]
    url: Optional[str]
    hide_url: Optional[bool]
    description: Optional[str]
    thumb_url: Optional[str]
    thumb_width: Optional[int]
    thumb_height: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultPhoto(BaseTelegram):
    type: str
    td: str
    photo_url: str
    thumb_url: str
    photo_width: Optional[int]
    photo_height: Optional[int]
    title: Optional[str]
    description: Optional[str]
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultGif(BaseTelegram):
    type: str
    id: str
    gif_url: str
    gif_width: Optional[int]
    gif_height: Optional[int]
    thumb_url: str
    title: Optional[str]
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultMpeg4Gif(BaseTelegram):
    type: str
    id: str
    mpeg4_url: str
    mpeg4_width: Optional[int]
    mpeg4_height: Optional[int]
    thumb_url: str
    title: Optional[str]
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultVideo(BaseTelegram):
    type: str
    id: str
    video_url: str
    mime_type: str
    thumb_url: str
    title: str
    caption: Optional[str]
    video_width: Optional[int]
    video_height: Optional[int]
    video_duration: Optional[int]
    description: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultAudio(BaseTelegram):
    type: str
    id: str
    audio_url: str
    title: str
    caption: Optional[str]
    performer: Optional[str]
    audio_duration: Optional[int]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultVoice(BaseTelegram):
    type: str
    id: str
    voice_url: str
    title: str
    caption: Optional[str]
    voice_duration: Optional[int]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultDocument(BaseTelegram):
    type: str
    id: str
    title: str
    caption: Optional[str]
    document_url: str
    mime_type: str
    description: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']
    thumb_url: Optional[str]
    thumb_width: Optional[int]
    thumb_height: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultLocation(BaseTelegram):
    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']
    thumb_url: Optional[str]
    thumb_width: Optional[int]
    thumb_height: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultVenue(BaseTelegram):
    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: Optional[str]
    foursquare_type: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']
    thumb_url: Optional[str]
    thumb_width: Optional[int]
    thumb_height: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultContact(BaseTelegram):
    type: str
    id: str
    phone_number: str
    first_name: str
    last_name: Optional[str]
    vcard: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']
    thumb_url: Optional[str]
    thumb_width: Optional[int]
    thumb_height: Optional[int]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultGame(BaseTelegram):
    type: str
    id: str
    game_short_name: str
    reply_markup: Optional[InlineKeyboardMarkup]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultCachedPhoto(BaseTelegram):
    type: str
    id: str
    photofileid: str
    title: Optional[str]
    description: Optional[str]
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultCachedGif(BaseTelegram):
    type: str
    id: str
    gif_file_id: str
    title: Optional[str]
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultCachedMpeg4Gif(BaseTelegram):
    type: str
    id: str
    mpeg4_file_id: str
    title: Optional[str]
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultCachedSticker(BaseTelegram):
    type: str
    id: str
    sticker_file_id: str
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultCachedDocument(BaseTelegram):
    type: str
    id: str
    title: str
    document_file_id: str
    description: Optional[str]
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultCachedVideo(BaseTelegram):
    type: str
    id: str
    video_file_id: str
    title: str
    description: Optional[str]
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultCachedVoice(BaseTelegram):
    type: str
    id: str
    voice_file_id: str
    title: str
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InlineQueryResultCachedAudio(BaseTelegram):
    type: str
    id: str
    audio_file_id: str
    caption: Optional[str]
    reply_markup: Optional[InlineKeyboardMarkup]
    input_message_content: Optional['InputMessageContent']


InputMessageContent = Union['InputTextMessageContent',
                            'InputLocationMessageContent',
                            'InputVenueMessageContent',
                            'InputContactMessageContent']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InputTextMessageContent(BaseTelegram):
    message_text: str
    parse_mode: str
    disable_web_page_preview: Optional[bool]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InputLocationMessageContent(BaseTelegram):
    latitude: float
    longitude: float


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InputVenueMessageContent(BaseTelegram):
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: Optional[str]
    foursquare_type: Optional[str]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class InputContactMessageContent(BaseTelegram):
    phone_number: str
    first_name: str
    last_name: Optional[str]
    vcard: Optional[str]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ChosenInlineResult(BaseTelegram):
    result_id: str
    from_: User
    location: Optional[Location]
    inline_message_id: Optional[str]
    query: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class LabeledPrice(BaseTelegram):
    label: str
    amount: int


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Invoice(BaseTelegram):
    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ShippingAddress(BaseTelegram):
    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class OrderInfo(BaseTelegram):
    name: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]
    shipping_address: Optional[ShippingAddress]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ShippingOption(BaseTelegram):
    id: str
    title: str
    prices: Tuple[LabeledPrice, ...]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class SuccessfulPayment(BaseTelegram):
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: Optional[str]
    order_info: Optional[OrderInfo]
    telegram_payment_charge_id: str
    provider_payment_charge_id: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class ShippingQuery(BaseTelegram):
    id: str
    from_: User
    invoice_payload: str
    shipping_address: ShippingAddress


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PreCheckoutQuery(BaseTelegram):
    id: str
    from_: User
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: Optional[str]
    order_info: Optional[OrderInfo]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportData(BaseTelegram):
    data: Tuple['EncryptedPassportElement', ...]
    credentials: 'EncryptedCredentials'


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportFile(BaseTelegram):
    file_id: str
    file_unique_id: str
    file_size: int
    file_date: int


@attr.s(slots=True, frozen=True, auto_attribs=True)
class EncryptedPassportElement(BaseTelegram):
    type: str
    data: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]
    files: Optional[Tuple[PassportFile, ...]]
    front_side: Optional[PassportFile]
    reverse_side: Optional[PassportFile]
    selfie: Optional[PassportFile]
    translation: Optional[Tuple[PassportFile, ...]]
    hash: Optional[str]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class EncryptedCredentials(BaseTelegram):
    data: str
    hash: str
    secret: str


PassportElementError = Union['PassportElementErrorDataField',
                             'PassportElementErrorFrontSide',
                             'PassportElementErrorReverseSide',
                             'PassportElementErrorSelfie',
                             'PassportElementErrorFile',
                             'PassportElementErrorFiles',
                             'PassportElementErrorTranslationFile',
                             'PassportElementErrorTranslationFiles',
                             'PassportElementErrorUnspecified']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportElementErrorDataField(BaseTelegram):
    source: str
    type: str
    field_name: str
    data_hash: str
    message: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportElementErrorFrontSide(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportElementErrorReverseSide(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportElementErrorSelfie(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportElementErrorFile(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportElementErrorFiles(BaseTelegram):
    source: str
    type: str
    file_hashes: List[str]
    message: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportElementErrorTranslationFile(BaseTelegram):
    source: str
    type: str
    file_hash: str
    message: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportElementErrorTranslationFiles(BaseTelegram):
    source: str
    type: str
    file_hashes: List[str]
    message: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class PassportElementErrorUnspecified(BaseTelegram):
    source: str
    type: str
    element_hash: str
    message: str


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Game(BaseTelegram):
    title: str
    description: str
    photo: Tuple[PhotoSize, ...]
    text: Optional[str]
    text_entities: Optional[Tuple[MessageEntity, ...]]
    animation: Optional['Animation']


@attr.s(slots=True, frozen=True, auto_attribs=True)
class CallbackGame(BaseTelegram):
    pass


@attr.s(slots=True, frozen=True, auto_attribs=True)
class GameHighScore(BaseTelegram):
    position: int
    user: User
    score: int
