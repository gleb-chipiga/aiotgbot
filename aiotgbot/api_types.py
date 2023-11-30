import asyncio
from dataclasses import dataclass
from io import BufferedReader
from pathlib import Path
from typing import AsyncIterator, Final, Sequence, Union, cast

from msgspec import UNSET, Raw, Struct, UnsetType, field

from aiotgbot.constants import InputMediaType, ParseMode, PollType

__all__ = (
    "DataMappingError",
    "StreamFile",
    "LocalFile",
    "BaseTelegram",
    "ResponseParameters",
    "APIResponse",
    "Update",
    "WebhookInfo",
    "User",
    "Chat",
    "Message",
    "MessageId",
    "MessageEntity",
    "PhotoSize",
    "Audio",
    "Document",
    "Video",
    "Animation",
    "Voice",
    "VideoNote",
    "Contact",
    "Dice",
    "Location",
    "Venue",
    "ProximityAlertTriggered",
    "PollOption",
    "PollAnswer",
    "Poll",
    "UserProfilePhotos",
    "File",
    "ReplyMarkup",
    "ReplyKeyboardMarkup",
    "KeyboardButton",
    "KeyboardButtonPollType",
    "ReplyKeyboardRemove",
    "InlineKeyboardMarkup",
    "InlineKeyboardButton",
    "LoginUrl",
    "CallbackQuery",
    "ForceReply",
    "ChatPhoto",
    "ChatInviteLink",
    "ChatAdministratorRights",
    "ChatMember",
    "ChatMemberUpdated",
    "ChatPermissions",
    "ChatLocation",
    "BotCommand",
    "BotCommandScopeDefault",
    "BotCommandScopeAllPrivateChats",
    "BotCommandScopeAllGroupChats",
    "BotCommandScopeChatAdministrators",
    "BotCommandScopeChat",
    "BotCommandScopeAllChatAdministrators",
    "BotCommandScopeChatMember",
    "BotCommandScope",
    "MenuButton",
    "InputFile",
    "InputMedia",
    "InputMediaPhoto",
    "InputMediaVideo",
    "InputMediaAnimation",
    "InputMediaAudio",
    "InputMediaDocument",
    "InputSticker",
    "Sticker",
    "StickerSet",
    "MaskPosition",
    "InlineQuery",
    "InlineQueryResult",
    "InlineQueryResultArticle",
    "InlineQueryResultPhoto",
    "InlineQueryResultGif",
    "InlineQueryResultMpeg4Gif",
    "InlineQueryResultVideo",
    "InlineQueryResultAudio",
    "InlineQueryResultVoice",
    "InlineQueryResultDocument",
    "InlineQueryResultLocation",
    "InlineQueryResultVenue",
    "InlineQueryResultContact",
    "InlineQueryResultGame",
    "InlineQueryResultCachedPhoto",
    "InlineQueryResultCachedGif",
    "InlineQueryResultCachedMpeg4Gif",
    "InlineQueryResultCachedSticker",
    "InlineQueryResultCachedDocument",
    "InlineQueryResultCachedVideo",
    "InlineQueryResultCachedVoice",
    "InlineQueryResultCachedAudio",
    "InputMessageContent",
    "InputTextMessageContent",
    "InputLocationMessageContent",
    "InputVenueMessageContent",
    "InputContactMessageContent",
    "ChosenInlineResult",
    "SentWebAppMessage",
    "LabeledPrice",
    "Invoice",
    "ShippingAddress",
    "OrderInfo",
    "ShippingOption",
    "SuccessfulPayment",
    "ShippingQuery",
    "PreCheckoutQuery",
    "PassportData",
    "PassportFile",
    "EncryptedPassportElement",
    "EncryptedCredentials",
    "PassportElementError",
    "PassportElementErrorDataField",
    "PassportElementErrorFrontSide",
    "PassportElementErrorReverseSide",
    "PassportElementErrorSelfie",
    "PassportElementErrorFile",
    "PassportElementErrorFiles",
    "PassportElementErrorTranslationFile",
    "PassportElementErrorTranslationFiles",
    "PassportElementErrorUnspecified",
    "Game",
    "CallbackGame",
    "GameHighScore",
)


class DataMappingError(BaseException):
    pass


@dataclass(frozen=True)
class StreamFile:
    content: AsyncIterator[bytes]
    name: str
    content_type: str | None = None


class LocalFile:
    def __init__(
        self,
        path: str | Path,
        content_type: str | None = None,
    ) -> None:
        self._path: Final[Path] = (
            path if isinstance(path, Path) else Path(path)
        )
        self._content_type: Final[str | None] = content_type

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def content_type(self) -> str | None:
        return self._content_type

    @property
    async def content(self) -> AsyncIterator[bytes]:
        loop = asyncio.get_running_loop()
        reader = cast(
            BufferedReader,
            await loop.run_in_executor(
                None,
                self._path.open,
                "rb",
            ),
        )
        try:
            chunk = await loop.run_in_executor(
                None,
                reader.read,
                2**16,
            )
            while len(chunk) > 0:
                yield chunk
                chunk = await loop.run_in_executor(
                    None,
                    reader.read,
                    2**16,
                )
        finally:
            await loop.run_in_executor(None, reader.close)


InputFile = LocalFile | StreamFile


class BaseTelegram(Struct, frozen=True, omit_defaults=True):
    pass


class ResponseParameters(BaseTelegram, frozen=True):
    migrate_to_chat_id: int | None = None
    retry_after: int | None = None


class APIResponse(BaseTelegram, frozen=True):
    ok: bool
    result: Raw | UnsetType = UNSET
    error_code: int | None = None
    description: str | None = None
    parameters: ResponseParameters | None = None


class Update(BaseTelegram, frozen=True):
    update_id: int
    message: "Message | None" = None
    edited_message: "Message | None" = None
    channel_post: "Message | None" = None
    edited_channel_post: "Message | None" = None
    inline_query: "InlineQuery | None" = None
    chosen_inline_result: "ChosenInlineResult | None" = None
    callback_query: "CallbackQuery | None" = None
    shipping_query: "ShippingQuery | None" = None
    pre_checkout_query: "PreCheckoutQuery | None" = None
    poll: "Poll | None" = None
    poll_answer: "PollAnswer | None" = None
    my_chat_member: "ChatMemberUpdated | None" = None
    chat_member: "ChatMemberUpdated | None" = None
    chat_join_request: "ChatJoinRequest | None" = None


class WebhookInfo(BaseTelegram, frozen=True):
    allowed_updates: tuple[str, ...]
    url: str | None = None
    has_custom_certificate: bool | None = None
    pending_update_count: int | None = None
    ip_address: str | None = None
    last_error_date: int | None = None
    last_error_message: str | None = None
    last_synchronization_error_date: int | None = None
    max_connections: int | None = None


class User(BaseTelegram, frozen=True):
    id: int
    is_bot: bool
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool | None = None
    added_to_attachment_menu: bool | None = None
    can_join_groups: bool | None = None
    can_read_all_group_messages: bool | None = None
    supports_inline_queries: bool | None = None


class Chat(BaseTelegram, frozen=True):
    id: int
    type: str
    title: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    photo: "ChatPhoto | None" = None
    bio: str | None = None
    has_private_forwards: bool | None = None
    join_to_send_messages: bool | None = None
    join_by_request: bool | None = None
    description: str | None = None
    invite_link: str | None = None
    pinned_message: "Message | None" = None
    permissions: "ChatPermissions | None" = None
    slow_mode_delay: int | None = None
    has_protected_content: bool | None = None
    has_restricted_voice_and_video_messages: bool | None = None
    sticker_set_name: str | None = None
    can_set_sticker_set: bool | None = None
    linked_chat_id: int | None = None
    location: "ChatLocation | None" = None


class Message(BaseTelegram, frozen=True):
    message_id: int
    date: int
    chat: Chat
    from_: User | None = field(default=None, name="from")
    sender_chat: Chat | None = None
    forward_from: User | None = None
    forward_from_chat: Chat | None = None
    forward_from_message_id: int | None = None
    forward_signature: str | None = None
    forward_sender_name: str | None = None
    forward_date: int | None = None
    is_automatic_forward: bool | None = None
    reply_to_message: "Message | None" = None
    via_bot: User | None = None
    edit_date: int | None = None
    has_protected_content: bool | None = None
    media_group_id: str | None = None
    author_signature: str | None = None
    text: str | None = None
    entities: tuple["MessageEntity", ...] | None = None
    caption_entities: tuple["MessageEntity", ...] | None = None
    audio: "Audio | None" = None
    document: "Document | None" = None
    animation: "Animation | None" = None
    game: "Game | None" = None
    photo: tuple["PhotoSize", ...] | None = None
    sticker: "Sticker | None" = None
    video: "Video | None" = None
    voice: "Voice | None" = None
    video_note: "VideoNote | None" = None
    caption: str | None = None
    contact: "Contact | None" = None
    dice: "Dice | None" = None
    location: "Location | None" = None
    venue: "Venue | None" = None
    poll: "Poll | None" = None
    new_chat_members: tuple[User, ...] | None = None
    left_chat_member: User | None = None
    new_chat_title: str | None = None
    new_chat_photo: tuple["PhotoSize", ...] | None = None
    delete_chat_photo: bool | None = None
    group_chat_created: bool | None = None
    supergroup_chat_created: bool | None = None
    channel_chat_created: bool | None = None
    message_auto_delete_timer_changed: Union[
        "MessageAutoDeleteTimerChanged", None
    ] = None
    migrate_to_chat_id: int | None = None
    migrate_from_chat_id: int | None = None
    pinned_message: "Message | None" = None
    invoice: "Invoice | None" = None
    successful_payment: "SuccessfulPayment | None" = None
    connected_website: str | None = None
    passport_data: "PassportData | None" = None
    proximity_alert_triggered: "ProximityAlertTriggered | None" = None
    video_chat_scheduled: "VideoChatScheduled | None" = None
    video_chat_started: "VideoChatStarted | None" = None
    video_chat_ended: "VideoChatEnded | None" = None
    video_chat_participants_invited: Union[
        "VideoChatParticipantsInvited", None
    ] = None
    web_app_data: "WebAppData | None" = None
    reply_markup: "InlineKeyboardMarkup | None" = None


class MessageId(BaseTelegram, frozen=True):
    message_id: int


class MessageEntity(BaseTelegram, frozen=True):
    type: str
    offset: int
    length: int
    url: str | None = None
    user: User | None = None
    language: str | None = None
    custom_emoji_id: str | None = None


class PhotoSize(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: int


class Audio(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    duration: int
    performer: str | None = None
    title: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    thumb: PhotoSize | None = None


class Document(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    thumb: PhotoSize | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Video(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: PhotoSize | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Animation(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    thumb: PhotoSize | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Voice(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: str | None = None
    file_size: int | None = None


class VideoNote(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumb: PhotoSize | None = None
    file_size: int | None = None


class Contact(BaseTelegram, frozen=True):
    phone_number: str
    first_name: str
    last_name: str | None = None
    user_id: int | None = None
    vcard: int | None = None


class Dice(BaseTelegram, frozen=True):
    emoji: str
    value: int


class Location(BaseTelegram, frozen=True):
    longitude: float
    latitude: float
    horizontal_accuracy: float | None = None
    live_period: int | None = None
    heading: int | None = None
    proximity_alert_radius: int | None = None


class Venue(BaseTelegram, frozen=True):
    location: Location
    title: str
    address: str
    foursquare_id: str | None = None
    foursquare_type: str | None = None
    google_place_id: str | None = None
    google_place_type: str | None = None


class WebAppData(BaseTelegram, frozen=True):
    data: str
    button_text: str


class VideoChatStarted(BaseTelegram, frozen=True):
    pass


class VideoChatEnded(BaseTelegram, frozen=True):
    duration: int


class VideoChatParticipantsInvited(BaseTelegram, frozen=True):
    users: tuple[User, ...] | None = None


class ProximityAlertTriggered(BaseTelegram, frozen=True):
    traveler: User
    watcher: User
    distance: int


class MessageAutoDeleteTimerChanged(BaseTelegram, frozen=True):
    message_auto_delete_time: int


class VideoChatScheduled(BaseTelegram, frozen=True):
    start_date: int


class PollOption(BaseTelegram, frozen=True):
    text: str
    voter_count: int


class PollAnswer(BaseTelegram, frozen=True):
    poll_id: str
    user: User
    option_ids: tuple[int, ...]


class Poll(BaseTelegram, frozen=True):
    id: str
    question: str
    options: tuple[PollOption, ...]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type: str
    allows_multiple_answers: bool
    correct_option_id: int | None = None
    explanation: str | None = None
    explanation_entities: tuple[MessageEntity, ...] | None = None
    open_period: int | None = None
    close_date: int | None = None


class UserProfilePhotos(BaseTelegram, frozen=True):
    total_count: int
    photos: tuple[tuple[PhotoSize, ...], ...]


class File(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    file_size: int | None = None
    file_path: str | None = None


class WebAppInfo(BaseTelegram, frozen=True):
    url: str


ReplyMarkup = Union[
    "InlineKeyboardMarkup",
    "ReplyKeyboardMarkup",
    "ReplyKeyboardRemove",
    "ForceReply",
]


class ReplyKeyboardMarkup(BaseTelegram, frozen=True):
    keyboard: Sequence[Sequence["KeyboardButton"]]
    resize_keyboard: bool | None = None
    one_time_keyboard: bool | None = None
    input_field_placeholder: str | None = None
    selective: bool | None = None


class KeyboardButton(BaseTelegram, frozen=True):
    text: str
    request_contact: bool | None = None
    request_location: bool | None = None
    request_poll: "KeyboardButtonPollType | None" = None
    web_app: WebAppInfo | None = None


class KeyboardButtonPollType(BaseTelegram, frozen=True):
    type: PollType


class ReplyKeyboardRemove(BaseTelegram, frozen=True):
    remove_keyboard: bool
    selective: bool | None = None


class InlineKeyboardMarkup(BaseTelegram, frozen=True):
    inline_keyboard: Sequence[Sequence["InlineKeyboardButton"]]


class InlineKeyboardButton(BaseTelegram, frozen=True):
    text: str
    url: str | None = None
    login_url: "LoginUrl | None" = None
    callback_data: str | None = None
    web_app: WebAppInfo | None = None
    switch_inline_query: str | None = None
    switch_inline_query_current_chat: str | None = None
    callback_game: "CallbackGame | None" = None
    pay: bool | None = None


class LoginUrl(BaseTelegram, frozen=True):
    url: str
    forward_text: str | None = None
    bot_username: str | None = None
    request_write_access: bool | None = None


class CallbackQuery(BaseTelegram, frozen=True):
    id: str
    from_: User = field(name="from")
    chat_instance: str
    message: Message | None = None
    inline_message_id: str | None = None
    data: str | None = None
    game_short_name: str | None = None


class ForceReply(BaseTelegram, frozen=True):
    force_reply: bool
    input_field_placeholder: str | None = None
    selective: bool | None = None


class ChatPhoto(BaseTelegram, frozen=True):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_file_unique_id: str


class ChatInviteLink(BaseTelegram, frozen=True):
    invite_link: str
    creator: User
    creates_join_request: bool
    is_primary: bool
    is_revoked: bool
    name: str | None = None
    expire_date: int | None = None
    member_limit: int | None = None
    pending_join_request_count: int | None = None


class ChatAdministratorRights(BaseTelegram, frozen=True):
    is_anonymous: bool
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_messages: bool | None
    can_edit_messages: bool | None
    can_pin_messages: bool | None


class ChatMember(BaseTelegram, frozen=True):
    user: User
    status: str
    custom_title: str | None = None
    is_anonymous: bool | None = None
    until_date: int | None = None
    can_be_edited: bool | None = None
    can_manage_chat: bool | None = None
    can_change_info: bool | None = None
    can_post_messages: bool | None = None
    can_edit_messages: bool | None = None
    can_delete_messages: bool | None = None
    can_manage_video_chats: bool | None = None
    can_invite_users: bool | None = None
    can_restrict_members: bool | None = None
    can_pin_messages: bool | None = None
    can_promote_members: bool | None = None
    is_member: bool | None = None
    can_send_messages: bool | None = None
    can_send_media_messages: bool | None = None
    can_send_other_messages: bool | None = None
    can_add_web_page_previews: bool | None = None
    can_send_polls: bool | None = None


class ChatMemberUpdated(BaseTelegram, frozen=True):
    chat: Chat
    from_: User = field(name="from")
    date: int
    old_chat_member: ChatMember
    new_chat_member: ChatMember
    invite_link: ChatInviteLink | None = None


class ChatJoinRequest(BaseTelegram, frozen=True):
    chat: Chat
    from_: User = field(name="from")
    date: int
    bio: str | None = None
    invite_link: ChatInviteLink | None = None


class ChatPermissions(BaseTelegram, frozen=True):
    can_send_messages: bool | None = None
    can_send_media_messages: bool | None = None
    can_send_polls: bool | None = None
    can_send_other_messages: bool | None = None
    can_add_web_page_previews: bool | None = None
    can_change_info: bool | None = None
    can_invite_users: bool | None = None
    can_pin_messages: bool | None = None


class ChatLocation(BaseTelegram, frozen=True):
    location: Location
    address: str


class BotCommand(BaseTelegram, frozen=True):
    command: str
    description: str


class BotCommandScopeDefault(BaseTelegram, frozen=True, omit_defaults=False):
    type: str = "default"


class BotCommandScopeAllPrivateChats(
    BaseTelegram, frozen=True, omit_defaults=False
):
    type: str = "all_private_chats"


class BotCommandScopeAllGroupChats(
    BaseTelegram, frozen=True, omit_defaults=False
):
    type: str = "all_group_chats"


class BotCommandScopeAllChatAdministrators(
    BaseTelegram, frozen=True, omit_defaults=False
):
    type: str = "all_chat_administrators"


class BotCommandScopeChat(BaseTelegram, frozen=True, omit_defaults=False):
    chat_id: int | str
    type: str = "chat"


class BotCommandScopeChatAdministrators(
    BaseTelegram, frozen=True, omit_defaults=False
):
    chat_id: int | str
    type: str = "chat"


class BotCommandScopeChatMember(
    BaseTelegram, frozen=True, omit_defaults=False
):
    chat_id: int | str
    user_id: int
    type: str = "chat"


BotCommandScope = Union[
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeChat,
    BotCommandScopeChatAdministrators,
    BotCommandScopeChatMember,
]


class MenuButton(BaseTelegram, frozen=True):
    type: str
    text: str | None
    web_app: WebAppInfo | None


class InputMedia(BaseTelegram, frozen=True):
    media: str | InputFile
    caption: str | None = None
    parse_mode: str | None = None
    caption_entities: Sequence[MessageEntity] | None = None


class InputMediaPhoto(InputMedia, frozen=True):
    type: str = InputMediaType.PHOTO


class InputMediaVideo(InputMedia, frozen=True):
    type: str = InputMediaType.VIDEO
    thumb: str | None = None
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    supports_streaming: bool | None = None


class InputMediaAnimation(InputMedia, frozen=True):
    type: str = InputMediaType.ANIMATION
    thumb: str | None = None
    width: int | None = None
    height: int | None = None
    duration: int | None = None


class InputMediaAudio(InputMedia, frozen=True):
    type: str = InputMediaType.AUDIO
    thumb: str | None = None
    duration: int | None = None
    performer: str | None = None
    title: str | None = None


class InputMediaDocument(InputMedia, frozen=True):
    type: str = InputMediaType.DOCUMENT
    thumb: str | None = None
    disable_content_type_detection: bool | None = None


class InputSticker(BaseTelegram, frozen=True):
    sticker: str | InputFile
    emoji_list: tuple[str, ...]
    mask_position: "MaskPosition | None"
    keywords: tuple[str, ...] | None


class Sticker(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    type: str
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumb: PhotoSize | None = None
    emoji: str | None = None
    set_name: str | None = None
    premium_animation: File | None = None
    mask_position: "MaskPosition | None" = None
    custom_emoji_id: str | None = None
    file_size: int | None = None


class StickerSet(BaseTelegram, frozen=True):
    name: str
    title: str
    sticker_type: str
    is_animated: bool
    is_video: bool
    stickers: tuple[Sticker, ...]
    thumb: PhotoSize | None = None


class MaskPosition(BaseTelegram, frozen=True):
    point: str
    x_shift: float
    y_shift: float
    scale: float


class InlineQuery(BaseTelegram, frozen=True):
    id: str
    from_: User = field(name="from")
    query: str
    offset: str
    chat_type: str | None = None
    location: Location | None = None


InlineQueryResult = Union[
    "InlineQueryResultCachedAudio",
    "InlineQueryResultCachedDocument",
    "InlineQueryResultCachedGif",
    "InlineQueryResultCachedMpeg4Gif",
    "InlineQueryResultCachedPhoto",
    "InlineQueryResultCachedSticker",
    "InlineQueryResultCachedVideo",
    "InlineQueryResultCachedVoice",
    "InlineQueryResultArticle",
    "InlineQueryResultAudio",
    "InlineQueryResultContact",
    "InlineQueryResultGame",
    "InlineQueryResultDocument",
    "InlineQueryResultGif",
    "InlineQueryResultLocation",
    "InlineQueryResultMpeg4Gif",
    "InlineQueryResultPhoto",
    "InlineQueryResultVenue",
    "InlineQueryResultVideo",
    "InlineQueryResultVoice",
]


class InlineQueryResultArticle(BaseTelegram, frozen=True):
    type: str
    id: str
    title: str
    input_message_content: "InputMessageContent"
    reply_markup: InlineKeyboardMarkup | None = None
    url: str | None = None
    hide_url: bool | None = None
    description: str | None = None
    thumb_url: str | None = None
    thumb_width: int | None = None
    thumb_height: int | None = None


class InlineQueryResultPhoto(BaseTelegram, frozen=True):
    type: str
    td: str
    photo_url: str
    thumb_url: str
    photo_width: int | None = None
    photo_height: int | None = None
    title: str | None = None
    description: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultGif(BaseTelegram, frozen=True):
    type: str
    id: str
    gif_url: str
    thumb_url: str
    gif_width: int | None = None
    gif_height: int | None = None
    title: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultMpeg4Gif(BaseTelegram, frozen=True):
    type: str
    id: str
    mpeg4_url: str
    thumb_url: str
    mpeg4_width: int | None = None
    mpeg4_height: int | None = None
    title: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultVideo(BaseTelegram, frozen=True):
    type: str
    id: str
    video_url: str
    mime_type: str
    thumb_url: str
    title: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    video_width: int | None = None
    video_height: int | None = None
    video_duration: int | None = None
    description: str | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultAudio(BaseTelegram, frozen=True):
    type: str
    id: str
    audio_url: str
    title: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    performer: str | None = None
    audio_duration: int | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultVoice(BaseTelegram, frozen=True):
    type: str
    id: str
    voice_url: str
    title: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    voice_duration: int | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultDocument(BaseTelegram, frozen=True):
    type: str
    id: str
    title: str
    document_url: str
    mime_type: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    description: str | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None
    thumb_url: str | None = None
    thumb_width: int | None = None
    thumb_height: int | None = None


class InlineQueryResultLocation(BaseTelegram, frozen=True):
    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    horizontal_accuracy: float | None = None
    live_period: int | None = None
    heading: int | None = None
    proximity_alert_radius: int | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None
    thumb_url: str | None = None
    thumb_width: int | None = None
    thumb_height: int | None = None


class InlineQueryResultVenue(BaseTelegram, frozen=True):
    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: str | None = None
    foursquare_type: str | None = None
    google_place_id: str | None = None
    google_place_type: str | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None
    thumb_url: str | None = None
    thumb_width: int | None = None
    thumb_height: int | None = None


class InlineQueryResultContact(BaseTelegram, frozen=True):
    type: str
    id: str
    phone_number: str
    first_name: str
    last_name: str | None = None
    vcard: str | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None
    thumb_url: str | None = None
    thumb_width: int | None = None
    thumb_height: int | None = None


class InlineQueryResultGame(BaseTelegram, frozen=True):
    type: str
    id: str
    game_short_name: str
    reply_markup: InlineKeyboardMarkup | None = None


class InlineQueryResultCachedPhoto(BaseTelegram, frozen=True):
    type: str
    id: str
    photofileid: str
    title: str | None = None
    description: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedGif(BaseTelegram, frozen=True):
    type: str
    id: str
    gif_file_id: str
    title: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedMpeg4Gif(BaseTelegram, frozen=True):
    type: str
    id: str
    mpeg4_file_id: str
    title: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedSticker(BaseTelegram, frozen=True):
    type: str
    id: str
    sticker_file_id: str
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedDocument(BaseTelegram, frozen=True):
    type: str
    id: str
    title: str
    document_file_id: str
    description: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedVideo(BaseTelegram, frozen=True):
    type: str
    id: str
    video_file_id: str
    title: str
    description: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedVoice(BaseTelegram, frozen=True):
    type: str
    id: str
    voice_file_id: str
    title: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedAudio(BaseTelegram, frozen=True):
    type: str
    id: str
    audio_file_id: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


InputMessageContent = Union[
    "InputTextMessageContent",
    "InputLocationMessageContent",
    "InputVenueMessageContent",
    "InputContactMessageContent",
]


class InputTextMessageContent(BaseTelegram, frozen=True):
    message_text: str
    parse_mode: ParseMode | None = None
    entities: Sequence[MessageEntity] | None = None
    disable_web_page_preview: bool | None = None


class InputLocationMessageContent(BaseTelegram, frozen=True):
    latitude: float
    longitude: float
    horizontal_accuracy: float | None = None
    live_period: int | None = None
    heading: int | None = None
    proximity_alert_radius: int | None = None


class InputVenueMessageContent(BaseTelegram, frozen=True):
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: str | None = None
    foursquare_type: str | None = None
    google_place_id: str | None = None
    google_place_type: str | None = None


class InputContactMessageContent(BaseTelegram, frozen=True):
    phone_number: str
    first_name: str
    last_name: str | None = None
    vcard: str | None = None


class InputInvoiceMessageContent:
    title: str
    description: str
    payload: str
    provider_token: str
    currency: str
    prices: tuple["LabeledPrice", ...]
    max_tip_amount: int | None = None
    suggested_tip_amounts: tuple[int, ...] | None = None
    provider_data: str | None = None
    photo_url: str | None = None
    photo_size: int | None = None
    photo_width: int | None = None
    photo_height: int | None = None
    need_name: bool | None = None
    need_phone_number: bool | None = None
    need_email: bool | None = None
    need_shipping_address: bool | None = None
    send_phone_number_to_provider: bool | None = None
    send_email_to_provider: bool | None = None
    is_flexible: bool | None = None


class ChosenInlineResult(BaseTelegram, frozen=True):
    result_id: str
    from_: User = field(name="from")
    query: str
    location: Location | None = None
    inline_message_id: str | None = None


class SentWebAppMessage(BaseTelegram, frozen=True):
    inline_message_id: str | None


class LabeledPrice(BaseTelegram, frozen=True):
    label: str
    amount: int


class Invoice(BaseTelegram, frozen=True):
    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int


class ShippingAddress(BaseTelegram, frozen=True):
    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str


class OrderInfo(BaseTelegram, frozen=True):
    name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    shipping_address: ShippingAddress | None = None


class ShippingOption(BaseTelegram, frozen=True):
    id: str
    title: str
    prices: tuple[LabeledPrice, ...]


class SuccessfulPayment(BaseTelegram, frozen=True):
    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    shipping_option_id: str | None = None
    order_info: OrderInfo | None = None


class ShippingQuery(BaseTelegram, frozen=True):
    id: str
    from_: User = field(name="from")
    invoice_payload: str
    shipping_address: ShippingAddress


class PreCheckoutQuery(BaseTelegram, frozen=True):
    id: str
    from_: User = field(name="from")
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: str | None = None
    order_info: OrderInfo | None = None


class PassportData(BaseTelegram, frozen=True):
    data: tuple["EncryptedPassportElement", ...]
    credentials: "EncryptedCredentials"


class PassportFile(BaseTelegram, frozen=True):
    file_id: str
    file_unique_id: str
    file_date: int
    file_size: int | None = None


class EncryptedPassportElement(BaseTelegram, frozen=True):
    type: str
    data: str | None = None
    phone_number: str | None = None
    email: str | None = None
    files: tuple[PassportFile, ...] | None = None
    front_side: PassportFile | None = None
    reverse_side: PassportFile | None = None
    selfie: PassportFile | None = None
    translation: tuple[PassportFile, ...] | None = None
    hash: str | None = None


class EncryptedCredentials(BaseTelegram, frozen=True):
    data: str
    hash: str
    secret: str


PassportElementError = Union[
    "PassportElementErrorDataField",
    "PassportElementErrorFrontSide",
    "PassportElementErrorReverseSide",
    "PassportElementErrorSelfie",
    "PassportElementErrorFile",
    "PassportElementErrorFiles",
    "PassportElementErrorTranslationFile",
    "PassportElementErrorTranslationFiles",
    "PassportElementErrorUnspecified",
]


class PassportElementErrorDataField(BaseTelegram, frozen=True):
    source: str
    type: str
    field_name: str
    data_hash: str
    message: str


class PassportElementErrorFrontSide(BaseTelegram, frozen=True):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorReverseSide(BaseTelegram, frozen=True):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorSelfie(BaseTelegram, frozen=True):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorFile(BaseTelegram, frozen=True):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorFiles(BaseTelegram, frozen=True):
    source: str
    type: str
    file_hashes: Sequence[str]
    message: str


class PassportElementErrorTranslationFile(BaseTelegram, frozen=True):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorTranslationFiles(BaseTelegram, frozen=True):
    source: str
    type: str
    file_hashes: Sequence[str]
    message: str


class PassportElementErrorUnspecified(BaseTelegram, frozen=True):
    source: str
    type: str
    element_hash: str
    message: str


class Game(BaseTelegram, frozen=True):
    title: str
    description: str
    photo: tuple[PhotoSize, ...]
    text: str | None = None
    text_entities: tuple[MessageEntity, ...] | None = None
    animation: "Animation | None" = None


class CallbackGame(BaseTelegram, frozen=True):
    pass


class GameHighScore(BaseTelegram, frozen=True):
    position: int
    user: User
    score: int
