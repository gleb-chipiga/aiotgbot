import asyncio
from dataclasses import dataclass
from enum import StrEnum, unique
from io import BufferedReader
from pathlib import Path
from typing import AsyncIterator, Final, Sequence, Union, cast

from msgspec import UNSET, Raw, Struct, UnsetType, field

from aiotgbot.constants import ParseMode, PollType

__all__ = (
    "API",
    "APIResponse",
    "Animation",
    "Audio",
    "BotCommand",
    "BotCommandScope",
    "BotCommandScope",
    "BotCommandScopeAllChatAdministrators",
    "BotCommandScopeAllGroupChats",
    "BotCommandScopeAllPrivateChats",
    "BotCommandScopeChat",
    "BotCommandScopeChatAdministrators",
    "BotCommandScopeChatMember",
    "BotCommandScopeDefault",
    "CallbackGame",
    "CallbackQuery",
    "Chat",
    "ChatAdministratorRights",
    "ChatInviteLink",
    "ChatLocation",
    "ChatMember",
    "ChatMemberAdministrator",
    "ChatMemberBanned",
    "ChatMemberBase",
    "ChatMemberBase",
    "ChatMemberLeft",
    "ChatMemberMember",
    "ChatMemberOwner",
    "ChatMemberRestricted",
    "ChatMemberUpdated",
    "ChatPermissions",
    "ChatPhoto",
    "ChosenInlineResult",
    "Contact",
    "DataMappingError",
    "Dice",
    "Document",
    "EncryptedCredentials",
    "EncryptedPassportElement",
    "File",
    "ForceReply",
    "ForumTopic",
    "ForumTopicClosed",
    "ForumTopicCreated",
    "ForumTopicReopened",
    "Game",
    "GameHighScore",
    "InlineKeyboardButton",
    "InlineKeyboardMarkup",
    "InlineQuery",
    "InlineQueryResult",
    "InlineQueryResultArticle",
    "InlineQueryResultAudio",
    "InlineQueryResultCachedAudio",
    "InlineQueryResultCachedDocument",
    "InlineQueryResultCachedGif",
    "InlineQueryResultCachedMpeg4Gif",
    "InlineQueryResultCachedPhoto",
    "InlineQueryResultCachedSticker",
    "InlineQueryResultCachedVideo",
    "InlineQueryResultCachedVoice",
    "InlineQueryResultContact",
    "InlineQueryResultDocument",
    "InlineQueryResultGame",
    "InlineQueryResultGif",
    "InlineQueryResultLocation",
    "InlineQueryResultMpeg4Gif",
    "InlineQueryResultPhoto",
    "InlineQueryResultVenue",
    "InlineQueryResultVideo",
    "InlineQueryResultVoice",
    "InputContactMessageContent",
    "InputFile",
    "InputLocationMessageContent",
    "InputMedia",
    "InputMediaAnimation",
    "InputMediaAudio",
    "InputMediaDocument",
    "InputMediaPhoto",
    "InputMediaVideo",
    "InputMessageContent",
    "InputSticker",
    "InputTextMessageContent",
    "InputVenueMessageContent",
    "Invoice",
    "KeyboardButton",
    "KeyboardButtonPollType",
    "LabeledPrice",
    "LocalFile",
    "Location",
    "LoginUrl",
    "MaskPosition",
    "MenuButton",
    "Message",
    "MessageEntity",
    "MessageId",
    "OrderInfo",
    "PassportData",
    "PassportElementDataType",
    "PassportElementError",
    "PassportElementErrorDataField",
    "PassportElementErrorFile",
    "PassportElementErrorFiles",
    "PassportElementErrorFrontSide",
    "PassportElementErrorReverseSide",
    "PassportElementErrorSelfie",
    "PassportElementErrorTranslationFile",
    "PassportElementErrorTranslationFiles",
    "PassportElementErrorUnspecified",
    "PassportElementFileType",
    "PassportElementFrontSideType",
    "PassportElementReverseSideType",
    "PassportElementSelfieType",
    "PassportElementTranslationFileType",
    "PassportElementType",
    "PassportFile",
    "PhotoSize",
    "Poll",
    "PollAnswer",
    "PollOption",
    "PreCheckoutQuery",
    "ProximityAlertTriggered",
    "ReplyKeyboardMarkup",
    "ReplyKeyboardRemove",
    "ReplyMarkup",
    "ResponseParameters",
    "SentWebAppMessage",
    "ShippingAddress",
    "ShippingOption",
    "ShippingQuery",
    "Sticker",
    "StickerSet",
    "StreamFile",
    "SuccessfulPayment",
    "Update",
    "User",
    "UserProfilePhotos",
    "Venue",
    "Video",
    "VideoNote",
    "Voice",
    "WebhookInfo",
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


class API(Struct, frozen=True, omit_defaults=True):
    pass


class ResponseParameters(API, frozen=True):
    migrate_to_chat_id: int | None = None
    retry_after: int | None = None


class APIResponse(API, frozen=True):
    ok: bool
    result: Raw | UnsetType = UNSET
    error_code: int | None = None
    description: str | None = None
    parameters: ResponseParameters | None = None


class Update(API, frozen=True):
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


class WebhookInfo(API, frozen=True):
    allowed_updates: tuple[str, ...]
    url: str | None = None
    has_custom_certificate: bool | None = None
    pending_update_count: int | None = None
    ip_address: str | None = None
    last_error_date: int | None = None
    last_error_message: str | None = None
    last_synchronization_error_date: int | None = None
    max_connections: int | None = None


class User(API, frozen=True):
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


class Chat(API, frozen=True):
    id: int
    type: str
    title: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_forum: bool | None = None
    photo: "ChatPhoto | None" = None
    active_usernames: Sequence[str] | None = None
    emoji_status_custom_emoji_id: str | None = None
    bio: str | None = None
    has_private_forwards: bool | None = None
    join_to_send_messages: bool | None = None
    join_by_request: bool | None = None
    description: str | None = None
    invite_link: str | None = None
    pinned_message: "Message | None" = None
    permissions: "ChatPermissions | None" = None
    slow_mode_delay: int | None = None
    has_aggressive_anti_spam_enabled: bool | None = None
    has_hidden_members: bool | None = None
    has_protected_content: bool | None = None
    has_restricted_voice_and_video_messages: bool | None = None
    sticker_set_name: str | None = None
    can_set_sticker_set: bool | None = None
    linked_chat_id: int | None = None
    location: "ChatLocation | None" = None


class Message(API, frozen=True):
    message_id: int
    date: int
    chat: Chat
    message_thread_id: int | None = None
    from_: User | None = field(default=None, name="from")
    sender_chat: Chat | None = None
    forward_from: User | None = None
    forward_from_chat: Chat | None = None
    forward_from_message_id: int | None = None
    forward_signature: str | None = None
    forward_sender_name: str | None = None
    forward_date: int | None = None
    is_topic_message: bool | None = None
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
    has_media_spoiler: bool | None = None
    audio: "Audio | None" = None
    document: "Document | None" = None
    animation: "Animation | None" = None
    photo: tuple["PhotoSize", ...] | None = None
    sticker: "Sticker | None" = None
    video: "Video | None" = None
    voice: "Voice | None" = None
    video_note: "VideoNote | None" = None
    caption: str | None = None
    contact: "Contact | None" = None
    dice: "Dice | None" = None
    game: "Game | None" = None
    poll: "Poll | None" = None
    venue: "Venue | None" = None
    location: "Location | None" = None
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
    write_access_allowed: "WriteAccessAllowed | None" = None
    passport_data: "PassportData | None" = None
    proximity_alert_triggered: "ProximityAlertTriggered | None" = None
    forum_topic_created: "ForumTopicCreated | None" = None
    forum_topic_edited: "ForumTopicEdited | None" = None
    forum_topic_closed: "ForumTopicClosed | None" = None
    forum_topic_reopened: "ForumTopicReopened | None" = None
    general_forum_topic_hidden: "GeneralForumTopicHidden | None" = None
    general_forum_topic_unhidden: "GeneralForumTopicUnhidden | None" = None

    video_chat_scheduled: "VideoChatScheduled | None" = None
    video_chat_started: "VideoChatStarted | None" = None
    video_chat_ended: "VideoChatEnded | None" = None
    video_chat_participants_invited: Union[
        "VideoChatParticipantsInvited", None
    ] = None
    web_app_data: "WebAppData | None" = None
    reply_markup: "InlineKeyboardMarkup | None" = None


class MessageId(API, frozen=True):
    message_id: int


class MessageEntity(API, frozen=True):
    type: str
    offset: int
    length: int
    url: str | None = None
    user: User | None = None
    language: str | None = None
    custom_emoji_id: str | None = None


class PhotoSize(API, frozen=True):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: int


class Audio(API, frozen=True):
    file_id: str
    file_unique_id: str
    duration: int
    performer: str | None = None
    title: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    thumb: PhotoSize | None = None


class Document(API, frozen=True):
    file_id: str
    file_unique_id: str
    thumb: PhotoSize | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Video(API, frozen=True):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: PhotoSize | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Animation(API, frozen=True):
    file_id: str
    file_unique_id: str
    thumb: PhotoSize | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Voice(API, frozen=True):
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: str | None = None
    file_size: int | None = None


class VideoNote(API, frozen=True):
    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumb: PhotoSize | None = None
    file_size: int | None = None


class Contact(API, frozen=True):
    phone_number: str
    first_name: str
    last_name: str | None = None
    user_id: int | None = None
    vcard: int | None = None


class Dice(API, frozen=True):
    emoji: str
    value: int


class Location(API, frozen=True):
    longitude: float
    latitude: float
    horizontal_accuracy: float | None = None
    live_period: int | None = None
    heading: int | None = None
    proximity_alert_radius: int | None = None


class Venue(API, frozen=True):
    location: Location
    title: str
    address: str
    foursquare_id: str | None = None
    foursquare_type: str | None = None
    google_place_id: str | None = None
    google_place_type: str | None = None


class WebAppData(API, frozen=True):
    data: str
    button_text: str


class VideoChatStarted(API, frozen=True):
    pass


class VideoChatEnded(API, frozen=True):
    duration: int


class VideoChatParticipantsInvited(API, frozen=True):
    users: tuple[User, ...] | None = None


class ProximityAlertTriggered(API, frozen=True):
    traveler: User
    watcher: User
    distance: int


class MessageAutoDeleteTimerChanged(API, frozen=True):
    message_auto_delete_time: int


class ForumTopicCreated(API, frozen=True):
    name: str
    icon_color: int
    icon_custom_emoji_id: str | None = None


class ForumTopicClosed(API, frozen=True):
    name: str | None = None
    icon_custom_emoji_id: str | None = None


class ForumTopicEdited(API, frozen=True):
    name: str | None = None
    icon_custom_emoji_id: str | None = None


class ForumTopicReopened(API, frozen=True):
    pass


class GeneralForumTopicHidden(API, frozen=True):
    pass


class GeneralForumTopicUnhidden(API, frozen=True):
    pass


class WriteAccessAllowed(API, frozen=True):
    from_request: bool | None = None
    web_app_name: str | None = None
    from_attachment_menu: bool | None = None


class VideoChatScheduled(API, frozen=True):
    start_date: int


class PollOption(API, frozen=True):
    text: str
    voter_count: int


class PollAnswer(API, frozen=True):
    poll_id: str
    user: User
    option_ids: tuple[int, ...]


class Poll(API, frozen=True):
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


class UserProfilePhotos(API, frozen=True):
    total_count: int
    photos: tuple[tuple[PhotoSize, ...], ...]


class File(API, frozen=True):
    file_id: str
    file_unique_id: str
    file_size: int | None = None
    file_path: str | None = None


class WebAppInfo(API, frozen=True):
    url: str


ReplyMarkup = Union[
    "InlineKeyboardMarkup",
    "ReplyKeyboardMarkup",
    "ReplyKeyboardRemove",
    "ForceReply",
]


class ReplyKeyboardMarkup(API, frozen=True):
    keyboard: Sequence[Sequence["KeyboardButton"]]
    is_persistent: bool | None = None
    resize_keyboard: bool | None = None
    one_time_keyboard: bool | None = None
    input_field_placeholder: str | None = None
    selective: bool | None = None


class KeyboardButton(API, frozen=True):
    text: str
    request_contact: bool | None = None
    request_location: bool | None = None
    request_poll: "KeyboardButtonPollType | None" = None
    web_app: WebAppInfo | None = None


class KeyboardButtonPollType(API, frozen=True):
    type: PollType


class ReplyKeyboardRemove(API, frozen=True):
    remove_keyboard: bool
    selective: bool | None = None


class InlineKeyboardMarkup(API, frozen=True):
    inline_keyboard: Sequence[Sequence["InlineKeyboardButton"]]


class InlineKeyboardButton(API, frozen=True):
    text: str
    url: str | None = None
    login_url: "LoginUrl | None" = None
    callback_data: str | None = None
    web_app: WebAppInfo | None = None
    switch_inline_query: str | None = None
    switch_inline_query_current_chat: str | None = None
    callback_game: "CallbackGame | None" = None
    pay: bool | None = None


class LoginUrl(API, frozen=True):
    url: str
    forward_text: str | None = None
    bot_username: str | None = None
    request_write_access: bool | None = None


class CallbackQuery(API, frozen=True):
    id: str
    from_: User = field(name="from")
    chat_instance: str
    message: Message | None = None
    inline_message_id: str | None = None
    data: str | None = None
    game_short_name: str | None = None


class ForceReply(
    API,
    frozen=True,
    tag_field="force_reply",
    tag=True,
):
    input_field_placeholder: str | None = None
    selective: bool | None = None


class ChatPhoto(API, frozen=True):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_file_unique_id: str


class ChatInviteLink(API, frozen=True):
    invite_link: str
    creator: User
    creates_join_request: bool
    is_primary: bool
    is_revoked: bool
    name: str | None = None
    expire_date: int | None = None
    member_limit: int | None = None
    pending_join_request_count: int | None = None


class ChatAdministratorRights(API, frozen=True):
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
    can_manage_topics: bool | None


class ChatMemberBase(
    API,
    frozen=True,
    tag_field="status",
):
    user: User


class ChatMemberOwner(
    ChatMemberBase,
    frozen=True,
    tag="creator",
):
    is_anonymous: bool
    custom_title: str | None = None


class ChatMemberAdministrator(
    ChatMemberBase,
    frozen=True,
    tag="administrator",
):
    can_be_edited: bool
    is_anonymous: bool
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_messages: bool | None = None
    can_edit_messages: bool | None = None
    can_pin_messages: bool | None = None
    can_post_stories: bool | None = None
    can_edit_stories: bool | None = None
    can_delete_stories: bool | None = None
    can_manage_topics: bool | None = None
    custom_title: str | None = None


class ChatMemberMember(
    ChatMemberBase,
    frozen=True,
    tag="member",
):
    pass


class ChatMemberRestricted(
    ChatMemberBase,
    frozen=True,
    tag="restricted",
):
    is_member: bool
    can_send_messages: bool
    can_send_audios: bool
    can_send_documents: bool
    can_send_photos: bool
    can_send_videos: bool
    can_send_video_notes: bool
    can_send_voice_notes: bool
    can_send_polls: bool
    can_send_other_messages: bool
    can_add_web_page_previews: bool
    can_change_info: bool
    can_invite_users: bool
    can_pin_messages: bool
    can_manage_topics: bool
    until_date: int


class ChatMemberLeft(
    ChatMemberBase,
    frozen=True,
    tag="left",
):
    pass


class ChatMemberBanned(
    ChatMemberBase,
    frozen=True,
    tag="kicked",
):
    until_date: int


ChatMember = Union[
    ChatMemberOwner,
    ChatMemberAdministrator,
    ChatMemberMember,
    ChatMemberRestricted,
    ChatMemberLeft,
    ChatMemberBanned,
]


class ChatMemberUpdated(API, frozen=True):
    chat: Chat
    from_: User = field(name="from")
    date: int
    old_chat_member: ChatMember
    new_chat_member: ChatMember
    invite_link: ChatInviteLink | None = None


class ChatJoinRequest(API, frozen=True):
    chat: Chat
    from_: User = field(name="from")
    date: int
    bio: str | None = None
    invite_link: ChatInviteLink | None = None


class ChatPermissions(API, frozen=True):
    can_send_messages: bool | None = None
    can_send_media_messages: bool | None = None
    can_send_polls: bool | None = None
    can_send_other_messages: bool | None = None
    can_add_web_page_previews: bool | None = None
    can_change_info: bool | None = None
    can_invite_users: bool | None = None
    can_pin_messages: bool | None = None
    can_manage_topics: bool | None = None


class ChatLocation(API, frozen=True):
    location: Location
    address: str


class ForumTopic(API, frozen=True):
    message_thread_id: int
    name: str
    icon_color: int
    icon_custom_emoji_id: str | None = None


class BotCommand(API, frozen=True):
    command: str
    description: str


class BotCommandScope(
    API,
    frozen=True,
    tag_field="type",
):
    pass


class BotCommandScopeDefault(
    BotCommandScope,
    frozen=True,
    tag="default",
):
    pass


class BotCommandScopeAllPrivateChats(
    BotCommandScope,
    frozen=True,
    tag="all_private_chats",
):
    pass


class BotCommandScopeAllGroupChats(
    BotCommandScope,
    frozen=True,
    tag="all_group_chats",
):
    pass


class BotCommandScopeAllChatAdministrators(
    BotCommandScope,
    frozen=True,
    tag="all_chat_administrators",
):
    pass


class BotCommandScopeChat(
    BotCommandScope,
    frozen=True,
    tag="chat",
):
    chat_id: int | str


class BotCommandScopeChatAdministrators(
    BotCommandScope,
    frozen=True,
    tag="chat_administrators",
):
    chat_id: int | str


class BotCommandScopeChatMember(
    API,
    frozen=True,
    tag="chat_member",
):
    chat_id: int | str
    user_id: int


class MenuButton(API, frozen=True):
    type: str
    text: str | None
    web_app: WebAppInfo | None


class InputMedia(
    API,
    frozen=True,
    tag_field="type",
):
    media: str | InputFile
    caption: str | None = None
    parse_mode: str | None = None
    caption_entities: Sequence[MessageEntity] | None = None


class InputMediaPhoto(
    InputMedia,
    frozen=True,
    tag="photo",
):
    has_spoiler: bool | None = None


class InputMediaVideo(
    InputMedia,
    frozen=True,
    tag="video",
):
    thumb: str | None = None
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    supports_streaming: bool | None = None
    has_spoiler: bool | None = None


class InputMediaAnimation(
    InputMedia,
    frozen=True,
    tag="animation",
):
    thumb: str | None = None
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    has_spoiler: bool | None = None


class InputMediaAudio(
    InputMedia,
    frozen=True,
    tag="audio",
):
    thumb: str | None = None
    duration: int | None = None
    performer: str | None = None
    title: str | None = None


class InputMediaDocument(
    InputMedia,
    frozen=True,
    tag="document",
):
    thumb: str | None = None
    disable_content_type_detection: bool | None = None


class InputSticker(API, frozen=True):
    sticker: str | InputFile
    emoji_list: Sequence[str]
    mask_position: "MaskPosition | None"
    keywords: Sequence[str] | None


class Sticker(API, frozen=True):
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


class StickerSet(API, frozen=True):
    name: str
    title: str
    sticker_type: str
    is_animated: bool
    is_video: bool
    stickers: tuple[Sticker, ...]
    thumb: PhotoSize | None = None


class MaskPosition(API, frozen=True):
    point: str
    x_shift: float
    y_shift: float
    scale: float


class InlineQuery(API, frozen=True):
    id: str
    from_: User = field(name="from")
    query: str
    offset: str
    chat_type: str | None = None
    location: Location | None = None


class InlineQueryResult(
    API,
    frozen=True,
    tag_field="type",
):
    id: str


class InlineQueryResultArticle(
    InlineQueryResult,
    frozen=True,
    tag="article",
):
    title: str
    input_message_content: "InputMessageContent"
    reply_markup: InlineKeyboardMarkup | None = None
    url: str | None = None
    hide_url: bool | None = None
    description: str | None = None
    thumb_url: str | None = None
    thumb_width: int | None = None
    thumb_height: int | None = None


class InlineQueryResultPhoto(
    InlineQueryResult,
    frozen=True,
    tag="photo",
):
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


class InlineQueryResultGif(
    InlineQueryResult,
    frozen=True,
    tag="gif",
):
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


class InlineQueryResultMpeg4Gif(
    InlineQueryResult,
    frozen=True,
    tag="mpeg4_gif",
):
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


class InlineQueryResultVideo(
    InlineQueryResult,
    frozen=True,
    tag="video",
):
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


class InlineQueryResultAudio(
    InlineQueryResult,
    frozen=True,
    tag="audio",
):
    audio_url: str
    title: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    performer: str | None = None
    audio_duration: int | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultVoice(
    InlineQueryResult,
    frozen=True,
    tag="voice",
):
    voice_url: str
    title: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    voice_duration: int | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultDocument(
    InlineQueryResult,
    frozen=True,
    tag="document",
):
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


class InlineQueryResultLocation(
    InlineQueryResult,
    frozen=True,
    tag="location",
):
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


class InlineQueryResultVenue(
    InlineQueryResult,
    frozen=True,
    tag="venue",
):
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


class InlineQueryResultContact(
    InlineQueryResult,
    frozen=True,
    tag="contact",
):
    phone_number: str
    first_name: str
    last_name: str | None = None
    vcard: str | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None
    thumb_url: str | None = None
    thumb_width: int | None = None
    thumb_height: int | None = None


class InlineQueryResultGame(
    InlineQueryResult,
    frozen=True,
    tag="game",
):
    game_short_name: str
    reply_markup: InlineKeyboardMarkup | None = None


class InlineQueryResultCachedPhoto(
    InlineQueryResult,
    frozen=True,
    tag="photo",
):
    photofileid: str
    title: str | None = None
    description: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedGif(
    InlineQueryResult,
    frozen=True,
    tag="gif",
):
    gif_file_id: str
    title: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedMpeg4Gif(
    InlineQueryResult,
    frozen=True,
    tag="mpeg4_gif",
):
    mpeg4_file_id: str
    title: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedSticker(
    InlineQueryResult,
    frozen=True,
    tag="sticker",
):
    sticker_file_id: str
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedDocument(
    InlineQueryResult,
    frozen=True,
    tag="document",
):
    title: str
    document_file_id: str
    description: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedVideo(
    InlineQueryResult,
    frozen=True,
    tag="video",
):
    video_file_id: str
    title: str
    description: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedVoice(
    InlineQueryResult,
    frozen=True,
    tag="voice",
):
    voice_file_id: str
    title: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedAudio(
    InlineQueryResult,
    frozen=True,
    tag="audio",
):
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


class InputTextMessageContent(API, frozen=True):
    message_text: str
    parse_mode: ParseMode | None = None
    entities: Sequence[MessageEntity] | None = None
    disable_web_page_preview: bool | None = None


class InputLocationMessageContent(API, frozen=True):
    latitude: float
    longitude: float
    horizontal_accuracy: float | None = None
    live_period: int | None = None
    heading: int | None = None
    proximity_alert_radius: int | None = None


class InputVenueMessageContent(API, frozen=True):
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: str | None = None
    foursquare_type: str | None = None
    google_place_id: str | None = None
    google_place_type: str | None = None


class InputContactMessageContent(API, frozen=True):
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
    prices: Sequence["LabeledPrice"]
    max_tip_amount: int | None = None
    suggested_tip_amounts: Sequence[int] | None = None
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


class ChosenInlineResult(API, frozen=True):
    result_id: str
    from_: User = field(name="from")
    query: str
    location: Location | None = None
    inline_message_id: str | None = None


class SentWebAppMessage(API, frozen=True):
    inline_message_id: str | None


class LabeledPrice(API, frozen=True):
    label: str
    amount: int


class Invoice(API, frozen=True):
    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int


class ShippingAddress(API, frozen=True):
    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str


class OrderInfo(API, frozen=True):
    name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    shipping_address: ShippingAddress | None = None


class ShippingOption(API, frozen=True):
    id: str
    title: str
    prices: tuple[LabeledPrice, ...]


class SuccessfulPayment(API, frozen=True):
    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    shipping_option_id: str | None = None
    order_info: OrderInfo | None = None


class ShippingQuery(API, frozen=True):
    id: str
    from_: User = field(name="from")
    invoice_payload: str
    shipping_address: ShippingAddress


class PreCheckoutQuery(API, frozen=True):
    id: str
    from_: User = field(name="from")
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: str | None = None
    order_info: OrderInfo | None = None


class PassportData(API, frozen=True):
    data: tuple["EncryptedPassportElement", ...]
    credentials: "EncryptedCredentials"


class PassportFile(API, frozen=True):
    file_id: str
    file_unique_id: str
    file_date: int
    file_size: int | None = None


@unique
class PassportElementType(StrEnum):
    PERSONAL_DETAILS = "personal_details"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    IDENTITY_CARD = "identity_card"
    INTERNAL_PASSPORT = "internal_passport"
    ADDRESS = "address"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    RENTAL_AGREEMENT = "rental_agreement"
    PASSPORT_REGISTRATION = "passport_registration"
    TEMPORARY_REGISTRATION = "temporary_registration"
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"


class EncryptedPassportElement(API, frozen=True):
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


class EncryptedCredentials(API, frozen=True):
    data: str
    hash: str
    secret: str


class PassportElementError(
    API,
    frozen=True,
    tag_field="source",
):
    pass


@unique
class PassportElementDataType(StrEnum):
    PERSONAL_DETAILS = PassportElementType.PERSONAL_DETAILS
    PASSPORT = PassportElementType.PASSPORT
    DRIVER_LICENSE = PassportElementType.DRIVER_LICENSE
    IDENTITY_CARD = PassportElementType.IDENTITY_CARD
    INTERNAL_PASSPORT = PassportElementType.INTERNAL_PASSPORT
    ADDRESS = PassportElementType.ADDRESS


class PassportElementErrorDataField(
    PassportElementError,
    frozen=True,
    tag="data",
):
    type: PassportElementDataType
    field_name: str
    data_hash: str
    message: str


@unique
class PassportElementFrontSideType(StrEnum):
    PASSPORT = PassportElementType.PASSPORT
    DRIVER_LICENSE = PassportElementType.DRIVER_LICENSE
    IDENTITY_CARD = PassportElementType.IDENTITY_CARD
    INTERNAL_PASSPORT = PassportElementType.INTERNAL_PASSPORT


class PassportElementErrorFrontSide(
    PassportElementError,
    frozen=True,
    tag="front_side",
):
    type: PassportElementFrontSideType
    file_hash: str
    message: str


@unique
class PassportElementReverseSideType(StrEnum):
    DRIVER_LICENSE = PassportElementType.DRIVER_LICENSE
    IDENTITY_CARD = PassportElementType.IDENTITY_CARD


class PassportElementErrorReverseSide(
    PassportElementError,
    frozen=True,
    tag="reverse_side",
):
    type: PassportElementReverseSideType
    file_hash: str
    message: str


@unique
class PassportElementSelfieType(StrEnum):
    PASSPORT = PassportElementType.PASSPORT
    DRIVER_LICENSE = PassportElementType.DRIVER_LICENSE
    IDENTITY_CARD = PassportElementType.IDENTITY_CARD
    INTERNAL_PASSPORT = PassportElementType.INTERNAL_PASSPORT


class PassportElementErrorSelfie(
    PassportElementError,
    frozen=True,
    tag="selfie",
):
    type: PassportElementSelfieType
    file_hash: str
    message: str


@unique
class PassportElementFileType(StrEnum):
    UTILITY_BILL = PassportElementType.UTILITY_BILL
    BANK_STATEMENT = PassportElementType.BANK_STATEMENT
    RENTAL_AGREEMENT = PassportElementType.RENTAL_AGREEMENT
    PASSPORT_REGISTRATION = PassportElementType.PASSPORT_REGISTRATION
    TEMPORARY_REGISTRATION = PassportElementType.TEMPORARY_REGISTRATION


class PassportElementErrorFile(
    PassportElementError,
    frozen=True,
    tag="file",
):
    type: PassportElementFileType
    file_hash: str
    message: str


class PassportElementErrorFiles(
    PassportElementError,
    frozen=True,
    tag="files",
):
    type: PassportElementFileType
    file_hashes: Sequence[str]
    message: str


@unique
class PassportElementTranslationFileType(StrEnum):
    PASSPORT = PassportElementType.PASSPORT
    DRIVER_LICENSE = PassportElementType.DRIVER_LICENSE
    IDENTITY_CARD = PassportElementType.IDENTITY_CARD
    INTERNAL_PASSPORT = PassportElementType.INTERNAL_PASSPORT
    UTILITY_BILL = PassportElementType.UTILITY_BILL
    BANK_STATEMENT = PassportElementType.BANK_STATEMENT
    RENTAL_AGREEMENT = PassportElementType.RENTAL_AGREEMENT
    PASSPORT_REGISTRATION = PassportElementType.PASSPORT_REGISTRATION
    TEMPORARY_REGISTRATION = PassportElementType.TEMPORARY_REGISTRATION


class PassportElementErrorTranslationFile(
    PassportElementError,
    frozen=True,
    tag="translation_file",
):
    type: PassportElementTranslationFileType
    file_hash: str
    message: str


class PassportElementErrorTranslationFiles(
    PassportElementError,
    frozen=True,
    tag="translation_files",
):
    type: PassportElementTranslationFileType
    file_hashes: Sequence[str]
    message: str


class PassportElementErrorUnspecified(
    PassportElementError,
    frozen=True,
    tag="unspecified",
):
    type: PassportElementType
    element_hash: str
    message: str


class Game(API, frozen=True):
    title: str
    description: str
    photo: tuple[PhotoSize, ...]
    text: str | None = None
    text_entities: tuple[MessageEntity, ...] | None = None
    animation: "Animation | None" = None


class CallbackGame(API, frozen=True):
    pass


class GameHighScore(API, frozen=True):
    position: int
    user: User
    score: int
