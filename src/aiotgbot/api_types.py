import asyncio
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from enum import StrEnum, unique
from io import BufferedReader
from pathlib import Path
from typing import Final, NewType, Protocol, Self, cast, runtime_checkable

import msgspec
from msgspec import UNSET, Raw, Struct, UnsetType, field
from yarl import URL

from .constants import ParseMode, PollType, StickerFormat

__all__ = (
    "API",
    "APIResponse",
    "Animation",
    "Attach",
    "Audio",
    "Birthdate",
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
    "BotDescription",
    "BotName",
    "BotShortDescription",
    "BusinessConnection",
    "BusinessIntro",
    "BusinessLocation",
    "BusinessMessagesDeleted",
    "BusinessOpeningHours",
    "BusinessOpeningHoursInterval",
    "CallbackGame",
    "CallbackQuery",
    "CallbackQueryId",
    "Chat",
    "ChatAdministratorRights",
    "ChatBoost",
    "ChatBoostRemoved",
    "ChatBoostSource",
    "ChatBoostSourceGiftCode",
    "ChatBoostSourceGiveaway",
    "ChatBoostSourcePremium",
    "ChatBoostUpdated",
    "ChatId",
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
    "ChatTitle",
    "ChosenInlineResult",
    "Contact",
    "DataMappingError",
    "Dice",
    "Document",
    "DocumentMimeType",
    "EncryptedCredentials",
    "EncryptedPassportElement",
    "ExternalReplyInfo",
    "File",
    "FileId",
    "FileUniqueId",
    "FirstName",
    "ForceReply",
    "ForumTopic",
    "ForumTopicClosed",
    "ForumTopicCreated",
    "ForumTopicReopened",
    "Game",
    "GameHighScore",
    "Giveaway",
    "GiveawayCompleted",
    "GiveawayCreated",
    "GiveawayWinners",
    "InlineKeyboardButton",
    "InlineKeyboardMarkup",
    "InlineQuery",
    "InlineQueryId",
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
    "InlineQueryResultsButton",
    "InputContactMessageContent",
    "InputFile",
    "InputLocationMessageContent",
    "InputMedia",
    "InputMediaAnimation",
    "InputMediaAudio",
    "InputMediaDocument",
    "InputMediaPhoto",
    "InputMediaVideo",
    "InputMediaWithThumbnail",
    "InputMessageContent",
    "InputSticker",
    "InputTextMessageContent",
    "InputVenueMessageContent",
    "Invoice",
    "KeyboardButton",
    "KeyboardButtonPollType",
    "KeyboardButtonRequestChat",
    "KeyboardButtonRequestUsers",
    "LabeledPrice",
    "LanguageCode",
    "LastName",
    "LinkPreviewOptions",
    "LocalFile",
    "Location",
    "LoginUrl",
    "MaskPosition",
    "MenuButton",
    "Message",
    "MessageEntity",
    "MessageId",
    "MessageOrigin",
    "MessageOriginChannel",
    "MessageOriginChat",
    "MessageOriginHiddenUser",
    "MessageOriginUser",
    "MessageReactionCountUpdated",
    "MessageReactionUpdated",
    "MessageThreadId",
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
    "ReactionCount",
    "ReactionType",
    "ReactionTypeCustomEmoji",
    "ReactionTypeEmoji",
    "ReplyKeyboardMarkup",
    "ReplyKeyboardRemove",
    "ReplyMarkup",
    "ReplyParameters",
    "ResponseMessageId",
    "ResponseParameters",
    "SentWebAppMessage",
    "SharedUser",
    "ShippingAddress",
    "ShippingOption",
    "ShippingQuery",
    "Sticker",
    "StickerSet",
    "StreamFile",
    "SuccessfulPayment",
    "SwitchInlineQueryChosenChat",
    "TextQuote",
    "ThumbnailMimeType",
    "URLString",
    "Update",
    "User",
    "UserChatBoosts",
    "UserId",
    "UserProfilePhotos",
    "Username",
    "UsersShared",
    "Venue",
    "Video",
    "VideoMimeType",
    "VideoNote",
    "Voice",
    "WebAppInfo",
    "WebhookInfo",
)


class DataMappingError(BaseException):
    pass


@runtime_checkable
class InputFile(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def content_type(self) -> str | None: ...

    @property
    def content(self) -> AsyncIterator[bytes]: ...


@dataclass(frozen=True, kw_only=True)
class StreamFile:
    name: str
    content: AsyncIterator[bytes]
    content_type: str | None = None


class LocalFile:
    def __init__(
        self,
        path: str | Path,
        content_type: str | None = None,
    ) -> None:
        self._path: Final[Path] = path if isinstance(path, Path) else Path(path)
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


class API(Struct, frozen=True, omit_defaults=True):
    pass

    def to_builtins(self) -> object:
        return cast(object, msgspec.to_builtins(self))

    @classmethod
    def convert(cls, obj: object) -> Self:
        return msgspec.convert(obj, cls)


class ResponseParameters(API, frozen=True, kw_only=True):
    migrate_to_chat_id: "ChatId | None" = None
    retry_after: int | None = None


class APIResponse(API, frozen=True, kw_only=True):
    ok: bool
    result: Raw | UnsetType = UNSET
    error_code: int | None = None
    description: str | None = None
    parameters: ResponseParameters | None = None


class Update(API, frozen=True, kw_only=True):
    update_id: int
    message: "Message | None" = None
    edited_message: "Message | None" = None
    channel_post: "Message | None" = None
    edited_channel_post: "Message | None" = None
    message_reaction: "MessageReactionUpdated | None" = None
    message_reaction_count: "MessageReactionCountUpdated | None" = None
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
    business_connection: "BusinessConnection | None" = None
    business_message: "Message | None" = None
    edited_business_message: "Message | None" = None
    deleted_business_messages: "BusinessMessagesDeleted | None" = None


class WebhookInfo(API, frozen=True, kw_only=True):
    url: str
    has_custom_certificate: bool
    pending_update_count: int
    ip_address: str | None = None
    last_error_date: int | None = None
    last_error_message: str | None = None
    last_synchronization_error_date: int | None = None
    max_connections: int | None = None
    allowed_updates: tuple[str, ...] | None = None


UserId = NewType("UserId", int)
FirstName = NewType("FirstName", str)
LastName = NewType("LastName", str)
Username = NewType("Username", str)
LanguageCode = NewType("LanguageCode", str)


class User(API, frozen=True, kw_only=True):
    id: UserId
    is_bot: bool
    first_name: FirstName
    last_name: LastName | None = None
    username: Username | None = None
    language_code: LanguageCode | None = None
    is_premium: bool | None = None
    added_to_attachment_menu: bool | None = None
    can_join_groups: bool | None = None
    can_read_all_group_messages: bool | None = None
    supports_inline_queries: bool | None = None
    can_connect_to_business: bool | None = None


ChatId = NewType("ChatId", int)
ChatTitle = NewType("ChatTitle", str)


class Chat(API, frozen=True, kw_only=True):
    id: ChatId
    type: str
    title: ChatTitle | None = None
    username: Username | None = None
    first_name: FirstName | None = None
    last_name: LastName | None = None
    is_forum: bool | None = None
    photo: "ChatPhoto | None" = None
    active_usernames: Sequence[str] | None = None
    available_reactions: tuple["ReactionType", ...] | None = None
    accent_color_id: int | None = None
    background_custom_emoji_id: str | None = None
    profile_accent_color_id: int | None = None
    profile_background_custom_emoji_id: str | None = None
    emoji_status_custom_emoji_id: str | None = None
    emoji_status_expiration_date: int | None = None
    bio: str | None = None
    has_private_forwards: bool | None = None
    has_restricted_voice_and_video_messages: bool | None = None
    join_to_send_messages: bool | None = None
    join_by_request: bool | None = None
    description: str | None = None
    invite_link: str | None = None
    pinned_message: "Message | None" = None
    permissions: "ChatPermissions | None" = None
    slow_mode_delay: int | None = None
    unrestrict_boost_count: int | None = None
    has_aggressive_anti_spam_enabled: bool | None = None
    has_hidden_members: bool | None = None
    has_protected_content: bool | None = None
    has_visible_history: bool | None = None
    sticker_set_name: str | None = None
    can_set_sticker_set: bool | None = None
    custom_emoji_sticker_set_name: str | None = None
    linked_chat_id: ChatId | None = None
    location: "ChatLocation | None" = None
    business_intro: "BusinessIntro | None" = None
    business_location: "BusinessLocation | None" = None
    business_opening_hours: "BusinessOpeningHours | None" = None
    personal_chat: "Chat | None" = None
    birthdate: "Birthdate | None" = None


class Birthdate(API, frozen=True, kw_only=True):
    day: int
    month: int
    year: int | None = None


class BusinessIntro(API, frozen=True, kw_only=True):
    title: str | None = None
    message: str | None = None


class BusinessLocation(API, frozen=True, kw_only=True):
    address: str
    location: "Location | None" = None


class BusinessOpeningHoursInterval(API, frozen=True, kw_only=True):
    opening_minute: int
    closing_minute: int
    weekday: int


class BusinessOpeningHours(API, frozen=True, kw_only=True):
    time_zone_name: str
    opening_hours: tuple["BusinessOpeningHoursInterval", ...]


class BusinessConnection(API, frozen=True, kw_only=True):
    id: str
    user: User
    user_chat_id: ChatId
    date: int
    can_reply: bool | None = None
    is_enabled: bool


class BusinessMessagesDeleted(API, frozen=True, kw_only=True):
    business_connection_id: str
    chat: Chat
    message_ids: tuple["MessageId", ...]


MessageId = NewType("MessageId", int)
MessageThreadId = NewType("MessageThreadId", int)


class Message(API, frozen=True, kw_only=True):
    message_id: MessageId
    message_thread_id: MessageThreadId | None = None
    from_: User | None = field(default=None, name="from")
    sender_chat: Chat | None = None
    business_connection_id: str | None = None
    sender_business_bot: User | None = None
    sender_boost_count: int | None = None
    date: int
    chat: Chat
    forward_origin: "MessageOrigin | None" = None
    is_topic_message: bool | None = None
    is_automatic_forward: bool | None = None
    is_from_offline: bool | None = None
    reply_to_message: "Message | None" = None
    external_reply: "ExternalReplyInfo | None" = None
    quote: "TextQuote | None" = None
    reply_to_story: "Story | None" = None
    via_bot: User | None = None
    edit_date: int | None = None
    has_protected_content: bool | None = None
    media_group_id: str | None = None
    author_signature: str | None = None
    text: str | None = None
    entities: tuple["MessageEntity", ...] | None = None
    link_preview_options: "LinkPreviewOptions | None" = None
    animation: "Animation | None" = None
    audio: "Audio | None" = None
    document: "Document | None" = None
    photo: tuple["PhotoSize", ...] | None = None
    sticker: "Sticker | None" = None
    story: "Story | None" = None
    video: "Video | None" = None
    video_note: "VideoNote | None" = None
    voice: "Voice | None" = None
    caption: str | None = None
    caption_entities: tuple["MessageEntity", ...] | None = None
    has_media_spoiler: bool | None = None
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
    message_auto_delete_timer_changed: "MessageAutoDeleteTimerChanged | None" = None
    migrate_to_chat_id: ChatId | None = None
    migrate_from_chat_id: ChatId | None = None
    pinned_message: "Message | None" = None
    invoice: "Invoice | None" = None
    successful_payment: "SuccessfulPayment | None" = None
    users_shared: "UsersShared | None" = None
    chat_shared: "ChatShared | None" = None
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
    giveaway_created: "GiveawayCreated | None" = None
    giveaway: "Giveaway | None" = None
    giveaway_winners: "GiveawayWinners | None" = None
    giveaway_completed: "GiveawayCompleted | None" = None
    video_chat_scheduled: "VideoChatScheduled | None" = None
    video_chat_started: "VideoChatStarted | None" = None
    video_chat_ended: "VideoChatEnded | None" = None
    video_chat_participants_invited: "VideoChatParticipantsInvited | None" = None
    web_app_data: "WebAppData | None" = None
    reply_markup: "InlineKeyboardMarkup | None" = None

    @property
    def is_inaccessible(self) -> bool:
        return self.date == 0


class ResponseMessageId(API, frozen=True):
    message_id: MessageId


class MessageEntity(API, frozen=True, kw_only=True):
    type: str
    offset: int
    length: int
    url: str | None = None
    user: User | None = None
    language: str | None = None
    custom_emoji_id: str | None = None


class TextQuote(API, frozen=True, kw_only=True):
    text: str
    entities: tuple["MessageEntity", ...] | None = None
    position: int
    is_manual: bool | None = None


class ExternalReplyInfo(API, frozen=True, kw_only=True):
    origin: "MessageOrigin"
    chat: Chat | None = None
    message_id: MessageId | None = None
    link_preview_options: "LinkPreviewOptions | None" = None
    animation: "Animation | None" = None
    audio: "Audio | None" = None
    document: "Document | None" = None
    photo: tuple["PhotoSize", ...] | None = None
    sticker: "Sticker | None" = None
    story: "Story | None" = None
    video: "Video | None" = None
    video_note: "VideoNote | None" = None
    voice: "Voice | None" = None
    has_media_spoiler: bool | None = None
    contact: "Contact | None" = None
    dice: "Dice | None" = None
    game: "Game | None" = None
    giveaway_created: "GiveawayCreated | None" = None
    giveaway: "Giveaway | None" = None
    giveaway_winners: "GiveawayWinners | None" = None
    invoice: "Invoice | None" = None
    location: "Location | None" = None
    poll: "Poll | None" = None
    venue: "Venue | None" = None


class ReplyParameters(API, frozen=True, kw_only=True):
    message_id: MessageId
    chat_id: ChatId | str | None = None
    allow_sending_without_reply: bool | None = None
    quote: str | None = None
    quote_parse_mode: str | None = None
    quote_entities: tuple["MessageEntity", ...] | None = None
    quote_position: int | None = None


class MessageOriginBase(
    API,
    frozen=True,
    tag_field="type",
    kw_only=True,
):
    date: int


class MessageOriginUser(
    MessageOriginBase,
    frozen=True,
    tag="user",
    kw_only=True,
):
    sender_user: User


class MessageOriginHiddenUser(
    MessageOriginBase,
    frozen=True,
    tag="hidden_user",
    kw_only=True,
):
    sender_user_name: str


class MessageOriginChat(
    MessageOriginBase,
    frozen=True,
    tag="chat",
    kw_only=True,
):
    sender_user_name: str
    sender_chat: Chat
    author_signature: str


class MessageOriginChannel(
    MessageOriginBase,
    frozen=True,
    tag="channel",
    kw_only=True,
):
    chat: Chat
    message_id: MessageId
    author_signature: str


MessageOrigin = (
    MessageOriginUser
    | MessageOriginHiddenUser
    | MessageOriginChat
    | MessageOriginChannel
)

FileId = NewType("FileId", str)
FileUniqueId = NewType("FileUniqueId", str)


class PhotoSize(API, frozen=True, kw_only=True):
    file_id: FileId
    file_unique_id: FileUniqueId
    width: int
    height: int
    file_size: int


class Audio(API, frozen=True, kw_only=True):
    file_id: FileId
    file_unique_id: FileUniqueId
    duration: int
    performer: str | None = None
    title: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    thumbnail: PhotoSize | None = None


class Document(API, frozen=True, kw_only=True):
    file_id: FileId
    file_unique_id: FileUniqueId
    thumbnail: PhotoSize | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Story(API, frozen=True):
    chat: Chat
    id: int


class Video(API, frozen=True, kw_only=True):
    file_id: FileId
    file_unique_id: FileUniqueId
    width: int
    height: int
    duration: int
    thumbnail: PhotoSize | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Animation(API, frozen=True, kw_only=True):
    file_id: FileId
    file_unique_id: FileUniqueId
    thumbnail: PhotoSize | None = None
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None


class Voice(API, frozen=True, kw_only=True):
    file_id: FileId
    file_unique_id: FileUniqueId
    duration: int
    mime_type: str | None = None
    file_size: int | None = None


class VideoNote(API, frozen=True, kw_only=True):
    file_id: FileId
    file_unique_id: FileUniqueId
    length: int
    duration: int
    thumbnail: PhotoSize | None = None
    file_size: int | None = None


class Contact(API, frozen=True, kw_only=True):
    phone_number: str
    first_name: str
    last_name: str | None = None
    user_id: UserId | None = None
    vcard: int | None = None


class Dice(API, frozen=True, kw_only=True):
    emoji: str
    value: int


class Location(API, frozen=True, kw_only=True):
    longitude: float
    latitude: float
    horizontal_accuracy: float | None = None
    live_period: int | None = None
    heading: int | None = None
    proximity_alert_radius: int | None = None


class Venue(API, frozen=True, kw_only=True):
    location: Location
    title: str
    address: str
    foursquare_id: str | None = None
    foursquare_type: str | None = None
    google_place_id: str | None = None
    google_place_type: str | None = None


class WebAppData(API, frozen=True, kw_only=True):
    data: str
    button_text: str


class VideoChatStarted(API, frozen=True):
    pass


class VideoChatEnded(API, frozen=True, kw_only=True):
    duration: int


class VideoChatParticipantsInvited(API, frozen=True, kw_only=True):
    users: tuple[User, ...] | None = None


class GiveawayCreated(API, frozen=True):
    pass


class Giveaway(API, frozen=True, kw_only=True):
    chats: tuple[Chat, ...]
    winners_selection_date: int
    winner_count: int
    only_new_members: bool | None = None
    has_public_winners: bool | None = None
    prize_description: str | None = None
    country_codes: tuple[str, ...] | None = None
    premium_subscription_month_count: int | None = None


class GiveawayWinners(API, frozen=True, kw_only=True):
    chat: Chat
    giveaway_message_id: MessageId
    winners_selection_date: int
    winner_count: int
    winners: tuple[User, ...]
    additional_chat_count: int | None = None
    premium_subscription_month_count: int | None = None
    unclaimed_prize_count: int | None = None
    only_new_members: bool | None = None
    was_refunded: bool | None = None
    prize_description: str | None = None


class GiveawayCompleted(API, frozen=True, kw_only=True):
    winner_count: int
    unclaimed_prize_count: int | None = None
    giveaway_message: Message | None = None


class ProximityAlertTriggered(API, frozen=True, kw_only=True):
    traveler: User
    watcher: User
    distance: int


class MessageAutoDeleteTimerChanged(API, frozen=True, kw_only=True):
    message_auto_delete_time: int


class ChatBoostAdded(API, frozen=True, kw_only=True):
    boost_count: int


class ForumTopicCreated(API, frozen=True, kw_only=True):
    name: str
    icon_color: int
    icon_custom_emoji_id: str | None = None


class ForumTopicClosed(API, frozen=True, kw_only=True):
    name: str | None = None
    icon_custom_emoji_id: str | None = None


class ForumTopicEdited(API, frozen=True, kw_only=True):
    name: str | None = None
    icon_custom_emoji_id: str | None = None


class ForumTopicReopened(API, frozen=True, kw_only=True):
    pass


class GeneralForumTopicHidden(API, frozen=True, kw_only=True):
    pass


class GeneralForumTopicUnhidden(API, frozen=True, kw_only=True):
    pass


class UsersShared(API, frozen=True, kw_only=True):
    request_id: int
    users: tuple["SharedUser", ...]


class SharedUser(API, frozen=True, kw_only=True):
    user_id: UserId | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: Username | None = None
    photo: "ChatPhoto | None" = None


class ChatShared(API, frozen=True, kw_only=True):
    request_id: int
    chat_id: ChatId
    title: ChatTitle | None = None
    username: Username | None = None
    photo: "ChatPhoto | None" = None


class WriteAccessAllowed(API, frozen=True, kw_only=True):
    from_request: bool | None = None
    web_app_name: str | None = None
    from_attachment_menu: bool | None = None


class VideoChatScheduled(API, frozen=True, kw_only=True):
    start_date: int


class PollOption(API, frozen=True, kw_only=True):
    text: str
    voter_count: int


class PollAnswer(API, frozen=True, kw_only=True):
    poll_id: str
    voter_chat: "Chat | None" = None
    user: User | None = None
    option_ids: tuple[int, ...]


class Poll(API, frozen=True, kw_only=True):
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


class LinkPreviewOptions(API, frozen=True, kw_only=True):
    is_disabled: bool | None = None
    url: str | None = None
    prefer_small_media: bool | None = None
    prefer_large_media: bool | None = None
    show_above_text: bool | None = None


class UserProfilePhotos(API, frozen=True, kw_only=True):
    total_count: int
    photos: tuple[tuple[PhotoSize, ...], ...]


class File(API, frozen=True, kw_only=True):
    file_id: FileId
    file_unique_id: FileUniqueId
    file_size: int | None = None
    file_path: str | None = None


class WebAppInfo(API, frozen=True, kw_only=True):
    url: str


class ReplyKeyboardMarkup(API, frozen=True, kw_only=True):
    keyboard: Sequence[Sequence["KeyboardButton"]]
    is_persistent: bool | None = None
    resize_keyboard: bool | None = None
    one_time_keyboard: bool | None = None
    input_field_placeholder: str | None = None
    selective: bool | None = None


class KeyboardButton(API, frozen=True, kw_only=True):
    text: str
    request_users: "KeyboardButtonRequestUsers | None" = None
    request_chat: "KeyboardButtonRequestChat | None" = None
    request_contact: bool | None = None
    request_location: bool | None = None
    request_poll: "KeyboardButtonPollType | None" = None
    web_app: WebAppInfo | None = None


class KeyboardButtonRequestUsers(API, frozen=True, kw_only=True):
    request_id: int
    user_is_bot: bool | None = None
    user_is_premium: bool | None = None
    request_name: bool | None = None
    request_username: bool | None = None
    request_photo: bool | None = None
    max_quantity: int | None = None


class KeyboardButtonRequestChat(API, frozen=True, kw_only=True):
    request_id: int
    chat_is_channel: bool
    chat_is_forum: bool | None = None
    chat_has_username: bool | None = None
    chat_is_created: bool | None = None
    request_title: bool | None = None
    request_username: bool | None = None
    request_photo: bool | None = None
    user_administrator_rights: "ChatAdministratorRights | None" = None
    bot_administrator_rights: "ChatAdministratorRights | None" = None
    bot_is_member: bool | None = None


class KeyboardButtonPollType(API, frozen=True, kw_only=True):
    type: PollType


class ReplyKeyboardRemove(API, frozen=True, kw_only=True):
    remove_keyboard: bool = field(default_factory=lambda: True)
    selective: bool | None = None


class InlineKeyboardMarkup(API, frozen=True):
    inline_keyboard: Sequence[Sequence["InlineKeyboardButton"]]


class SwitchInlineQueryChosenChat(API, frozen=True, kw_only=True):
    query: str | None = None
    allow_user_chats: bool | None = None
    allow_bot_chats: bool | None = None
    allow_group_chats: bool | None = None
    allow_channel_chats: bool | None = None


class InlineKeyboardButton(API, frozen=True, kw_only=True):
    text: str
    url: str | None = None
    login_url: "LoginUrl | None" = None
    callback_data: str | None = None
    web_app: WebAppInfo | None = None
    switch_inline_query: str | None = None
    switch_inline_query_current_chat: str | None = None
    switch_inline_query_chosen_chat: SwitchInlineQueryChosenChat | None = None
    callback_game: "CallbackGame | None" = None
    pay: bool | None = None


class LoginUrl(API, frozen=True, kw_only=True):
    url: str
    forward_text: str | None = None
    bot_username: str | None = None
    request_write_access: bool | None = None


CallbackQueryId = NewType("CallbackQueryId", str)


class CallbackQuery(API, frozen=True, kw_only=True):
    id: CallbackQueryId
    from_: User = field(name="from")
    message: Message | None = None
    inline_message_id: str | None = None
    chat_instance: str
    data: str | None = None
    game_short_name: str | None = None


class ForceReply(
    API,
    frozen=True,
    kw_only=True,
):
    force_reply: bool = field(default_factory=lambda: True)
    input_field_placeholder: str | None = None
    selective: bool | None = None


ReplyMarkup = (
    InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply
)


class ChatPhoto(API, frozen=True, kw_only=True):
    small_file_id: FileId
    small_file_unique_id: FileUniqueId
    big_file_id: FileId
    big_file_unique_id: FileUniqueId


class ChatInviteLink(API, frozen=True, kw_only=True):
    invite_link: str
    creator: User
    creates_join_request: bool
    is_primary: bool
    is_revoked: bool
    name: str | None = None
    expire_date: int | None = None
    member_limit: int | None = None
    pending_join_request_count: int | None = None


class ChatAdministratorRights(API, frozen=True, kw_only=True):
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


class ChatMemberBase(
    API,
    frozen=True,
    tag_field="status",
    kw_only=True,
):
    user: User


class ChatMemberOwner(
    ChatMemberBase,
    frozen=True,
    tag="creator",
    kw_only=True,
):
    is_anonymous: bool
    custom_title: str | None = None


class ChatMemberAdministrator(
    ChatMemberBase,
    frozen=True,
    tag="administrator",
    kw_only=True,
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
    kw_only=True,
):
    pass


class ChatMemberRestricted(
    ChatMemberBase,
    frozen=True,
    tag="restricted",
    kw_only=True,
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
    kw_only=True,
):
    pass


class ChatMemberBanned(
    ChatMemberBase,
    frozen=True,
    tag="kicked",
    kw_only=True,
):
    until_date: int


ChatMember = (
    ChatMemberOwner
    | ChatMemberAdministrator
    | ChatMemberMember
    | ChatMemberRestricted
    | ChatMemberLeft
    | ChatMemberBanned
)


class ChatMemberUpdated(API, frozen=True, kw_only=True):
    chat: Chat
    from_: User = field(name="from")
    date: int
    old_chat_member: ChatMember
    new_chat_member: ChatMember
    invite_link: ChatInviteLink | None = None
    via_chat_folder_invite_link: bool | None = None


class ChatJoinRequest(API, frozen=True, kw_only=True):
    chat: Chat
    from_: User = field(name="from")
    user_chat_id: ChatId
    date: int
    bio: str | None = None
    invite_link: ChatInviteLink | None = None


class ChatPermissions(API, frozen=True, kw_only=True):
    can_send_messages: bool | None = None
    can_send_audios: bool | None = None
    can_send_documents: bool | None = None
    can_send_photos: bool | None = None
    can_send_videos: bool | None = None
    can_send_video_notes: bool | None = None
    can_send_voice_notes: bool | None = None
    can_send_polls: bool | None = None
    can_send_other_messages: bool | None = None
    can_add_web_page_previews: bool | None = None
    can_change_info: bool | None = None
    can_invite_users: bool | None = None
    can_pin_messages: bool | None = None
    can_manage_topics: bool | None = None


class ChatLocation(API, frozen=True, kw_only=True):
    location: Location
    address: str


class ReactionTypeBase(
    API,
    frozen=True,
    tag_field="type",
    kw_only=True,
):
    pass


class ReactionTypeEmoji(
    ReactionTypeBase,
    frozen=True,
    tag="emoji",
    kw_only=True,
):
    emoji: str


class ReactionTypeCustomEmoji(
    ReactionTypeBase,
    frozen=True,
    tag="custom_emoji",
    kw_only=True,
):
    custom_emoji: str


ReactionType = ReactionTypeEmoji | ReactionTypeCustomEmoji


class ReactionCount(API, frozen=True, kw_only=True):
    type: ReactionType
    total_count: int


class MessageReactionUpdated(API, frozen=True, kw_only=True):
    chat: Chat
    message_id: MessageId
    user: User | None = None
    actor_chat: Chat | None = None
    date: int
    old_reaction: tuple[ReactionType, ...]
    new_reaction: tuple[ReactionType, ...]


class MessageReactionCountUpdated(API, frozen=True, kw_only=True):
    chat: Chat
    message_id: MessageId
    date: int
    reactions: tuple[ReactionCount, ...]


class ForumTopic(API, frozen=True, kw_only=True):
    message_thread_id: MessageThreadId
    name: str
    icon_color: int
    icon_custom_emoji_id: str | None = None


class BotCommand(API, frozen=True, kw_only=True):
    command: str
    description: str


class BotCommandScope(
    API,
    frozen=True,
    tag_field="type",
    kw_only=True,
):
    pass


class BotCommandScopeDefault(
    BotCommandScope,
    frozen=True,
    tag="default",
    kw_only=True,
):
    pass


class BotCommandScopeAllPrivateChats(
    BotCommandScope,
    frozen=True,
    tag="all_private_chats",
    kw_only=True,
):
    pass


class BotCommandScopeAllGroupChats(
    BotCommandScope,
    frozen=True,
    tag="all_group_chats",
    kw_only=True,
):
    pass


class BotCommandScopeAllChatAdministrators(
    BotCommandScope,
    frozen=True,
    tag="all_chat_administrators",
    kw_only=True,
):
    pass


class BotCommandScopeChat(
    BotCommandScope,
    frozen=True,
    tag="chat",
    kw_only=True,
):
    chat_id: ChatId | str


class BotCommandScopeChatAdministrators(
    BotCommandScope,
    frozen=True,
    tag="chat_administrators",
    kw_only=True,
):
    chat_id: ChatId | str


class BotCommandScopeChatMember(
    API,
    frozen=True,
    tag="chat_member",
    kw_only=True,
):
    chat_id: ChatId | str
    user_id: UserId


class BotName(API, frozen=True, kw_only=True):
    name: str


class BotDescription(API, frozen=True, kw_only=True):
    description: str


class BotShortDescription(API, frozen=True, kw_only=True):
    short_description: str


class MenuButton(API, frozen=True, kw_only=True):
    type: str
    text: str | None
    web_app: WebAppInfo | None


class ChatBoostSourceBase(
    API,
    frozen=True,
    tag_field="source",
    kw_only=True,
):
    pass


class ChatBoostSourcePremium(
    ChatBoostSourceBase,
    frozen=True,
    tag="premium",
    kw_only=True,
):
    user: User


class ChatBoostSourceGiftCode(
    ChatBoostSourceBase,
    frozen=True,
    tag="gift_code",
    kw_only=True,
):
    user: User


class ChatBoostSourceGiveaway(
    ChatBoostSourceBase,
    frozen=True,
    tag="giveaway",
    kw_only=True,
):
    giveaway_message_id: MessageId
    user: User | None = None
    is_unclaimed: bool | None = None


ChatBoostSource = (
    ChatBoostSourcePremium | ChatBoostSourceGiftCode | ChatBoostSourceGiveaway
)


class ChatBoost(API, frozen=True, kw_only=True):
    boost_id: str
    add_date: int
    expiration_date: int
    source: ChatBoostSource


class ChatBoostUpdated(API, frozen=True, kw_only=True):
    chat: Chat
    boost: ChatBoost


class ChatBoostRemoved(API, frozen=True, kw_only=True):
    chat: Chat
    boost_id: str
    remove_date: int
    source: ChatBoostSource


class UserChatBoosts(API, frozen=True, kw_only=True):
    boosts: tuple[ChatBoost, ...]


Attach = NewType("Attach", str)
URLString = NewType("URLString", str)


class InputMedia(
    API,
    frozen=True,
    tag_field="type",
    kw_only=True,
):
    media: FileId | URL | URLString | InputFile | Attach
    caption: str | None = None
    parse_mode: str | None = None
    caption_entities: Sequence[MessageEntity] | None = None


class InputMediaPhoto(
    InputMedia,
    frozen=True,
    tag="photo",
    kw_only=True,
):
    has_spoiler: bool | None = None


class InputMediaWithThumbnail(
    InputMedia,
    frozen=True,
    kw_only=True,
):
    thumbnail: InputFile | Attach | None = None


class InputMediaVideo(
    InputMediaWithThumbnail,
    frozen=True,
    tag="video",
    kw_only=True,
):
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    supports_streaming: bool | None = None
    has_spoiler: bool | None = None


class InputMediaAnimation(
    InputMediaWithThumbnail,
    frozen=True,
    tag="animation",
    kw_only=True,
):
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    has_spoiler: bool | None = None


class InputMediaAudio(
    InputMediaWithThumbnail,
    frozen=True,
    tag="audio",
    kw_only=True,
):
    duration: int | None = None
    performer: str | None = None
    title: str | None = None


class InputMediaDocument(
    InputMediaWithThumbnail,
    frozen=True,
    tag="document",
    kw_only=True,
):
    disable_content_type_detection: bool | None = None


class InputSticker(API, frozen=True):
    sticker: FileId | URL | URLString | InputFile | Attach
    format: StickerFormat
    emoji_list: Sequence[str]
    mask_position: "MaskPosition | None"
    keywords: Sequence[str] | None


class Sticker(API, frozen=True):
    file_id: FileId
    file_unique_id: FileUniqueId
    type: str
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumbnail: PhotoSize | None = None
    emoji: str | None = None
    set_name: str | None = None
    premium_animation: File | None = None
    mask_position: "MaskPosition | None" = None
    custom_emoji_id: str | None = None
    needs_repainting: bool | None = None
    file_size: int | None = None


class StickerSet(API, frozen=True):
    name: str
    title: str
    sticker_type: str
    stickers: tuple[Sticker, ...]
    thumbnail: PhotoSize | None = None


class MaskPosition(API, frozen=True):
    point: str
    x_shift: float
    y_shift: float
    scale: float


class InlineQueryResultsButton(API, frozen=True):
    text: str
    web_app: WebAppInfo | None = None
    start_parameter: str | None = None


InlineQueryId = NewType("InlineQueryId", str)


class InlineQuery(API, frozen=True):
    id: InlineQueryId
    from_: User = field(name="from")
    query: str
    offset: str
    chat_type: str | None = None
    location: Location | None = None


class InlineQueryResult(
    API,
    frozen=True,
    tag_field="type",
    kw_only=True,
):
    id: str


class InlineQueryResultArticle(
    InlineQueryResult,
    frozen=True,
    tag="article",
    kw_only=True,
):
    title: str
    input_message_content: "InputMessageContent"
    reply_markup: InlineKeyboardMarkup | None = None
    url: str | None = None
    hide_url: bool | None = None
    description: str | None = None
    thumbnail_url: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None


class InlineQueryResultPhoto(
    InlineQueryResult,
    frozen=True,
    tag="photo",
    kw_only=True,
):
    photo_url: str
    thumbnail_url: str
    photo_width: int | None = None
    photo_height: int | None = None
    title: str | None = None
    description: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


@unique
class ThumbnailMimeType(StrEnum):
    JPEG = "image/jpeg"
    GIF = "image/gif"
    MP4 = "video/mp4"


class InlineQueryResultGif(
    InlineQueryResult,
    frozen=True,
    tag="gif",
    kw_only=True,
):
    gif_url: str
    gif_width: int | None = None
    gif_height: int | None = None
    gif_duration: int | None = None
    thumbnail_url: str
    thumbnail_mime_type: ThumbnailMimeType | None = None
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
    kw_only=True,
):
    mpeg4_url: str
    mpeg4_width: int | None = None
    mpeg4_height: int | None = None
    mpeg4_duration: int | None = None
    thumbnail_url: str
    thumbnail_mime_type: ThumbnailMimeType | None = None
    title: str | None = None
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


@unique
class VideoMimeType(StrEnum):
    HTML = "text/html"
    MP4 = "video/mp4"


class InlineQueryResultVideo(
    InlineQueryResult,
    frozen=True,
    tag="video",
    kw_only=True,
):
    video_url: str
    mime_type: VideoMimeType
    thumbnail_url: str
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
    kw_only=True,
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
    kw_only=True,
):
    voice_url: str
    title: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    voice_duration: int | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


@unique
class DocumentMimeType(StrEnum):
    PDF = "application/pdf"
    ZIP = "application/zip"


class InlineQueryResultDocument(
    InlineQueryResult,
    frozen=True,
    tag="document",
    kw_only=True,
):
    title: str
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    document_url: str
    mime_type: DocumentMimeType
    description: str | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None
    thumbnail_url: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None


class InlineQueryResultLocation(
    InlineQueryResult,
    frozen=True,
    tag="location",
    kw_only=True,
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
    thumbnail_url: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None


class InlineQueryResultVenue(
    InlineQueryResult,
    frozen=True,
    tag="venue",
    kw_only=True,
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
    thumbnail_url: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None


class InlineQueryResultContact(
    InlineQueryResult,
    frozen=True,
    tag="contact",
    kw_only=True,
):
    phone_number: str
    first_name: str
    last_name: str | None = None
    vcard: str | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None
    thumbnail_url: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None


class InlineQueryResultGame(
    InlineQueryResult,
    frozen=True,
    tag="game",
    kw_only=True,
):
    game_short_name: str
    reply_markup: InlineKeyboardMarkup | None = None


class InlineQueryResultCachedPhoto(
    InlineQueryResult,
    frozen=True,
    tag="photo",
    kw_only=True,
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
    kw_only=True,
):
    gif_file_id: FileId
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
    kw_only=True,
):
    mpeg4_file_id: FileId
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
    kw_only=True,
):
    sticker_file_id: FileId
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InlineQueryResultCachedDocument(
    InlineQueryResult,
    frozen=True,
    tag="document",
    kw_only=True,
):
    title: str
    document_file_id: FileId
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
    kw_only=True,
):
    video_file_id: FileId
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
    kw_only=True,
):
    voice_file_id: FileId
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
    kw_only=True,
):
    audio_file_id: FileId
    caption: str | None = None
    parse_mode: ParseMode | None = None
    caption_entities: Sequence[MessageEntity] | None = None
    reply_markup: InlineKeyboardMarkup | None = None
    input_message_content: "InputMessageContent | None" = None


class InputTextMessageContent(API, frozen=True, kw_only=True):
    message_text: str
    parse_mode: ParseMode | None = None
    entities: Sequence[MessageEntity] | None = None
    link_preview_options: LinkPreviewOptions | None = None


class InputLocationMessageContent(API, frozen=True, kw_only=True):
    latitude: float
    longitude: float
    horizontal_accuracy: float | None = None
    live_period: int | None = None
    heading: int | None = None
    proximity_alert_radius: int | None = None


class InputVenueMessageContent(API, frozen=True, kw_only=True):
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: str | None = None
    foursquare_type: str | None = None
    google_place_id: str | None = None
    google_place_type: str | None = None


class InputContactMessageContent(API, frozen=True, kw_only=True):
    phone_number: str
    first_name: str
    last_name: str | None = None
    vcard: str | None = None


class InputInvoiceMessageContent(API, frozen=True, kw_only=True):
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


InputMessageContent = (
    InputTextMessageContent
    | InputLocationMessageContent
    | InputVenueMessageContent
    | InputContactMessageContent
)


class ChosenInlineResult(API, frozen=True, kw_only=True):
    result_id: str
    from_: User = field(name="from")
    query: str
    location: Location | None = None
    inline_message_id: str | None = None


class SentWebAppMessage(API, frozen=True, kw_only=True):
    inline_message_id: str | None


class LabeledPrice(API, frozen=True, kw_only=True):
    label: str
    amount: int


class Invoice(API, frozen=True, kw_only=True):
    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int


class ShippingAddress(API, frozen=True, kw_only=True):
    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str


class OrderInfo(API, frozen=True, kw_only=True):
    name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    shipping_address: ShippingAddress | None = None


class ShippingOption(API, frozen=True, kw_only=True):
    id: str
    title: str
    prices: tuple[LabeledPrice, ...]


class SuccessfulPayment(API, frozen=True, kw_only=True):
    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    shipping_option_id: str | None = None
    order_info: OrderInfo | None = None


class ShippingQuery(API, frozen=True, kw_only=True):
    id: str
    from_: User = field(name="from")
    invoice_payload: str
    shipping_address: ShippingAddress


class PreCheckoutQuery(API, frozen=True, kw_only=True):
    id: str
    from_: User = field(name="from")
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: str | None = None
    order_info: OrderInfo | None = None


class PassportData(API, frozen=True, kw_only=True):
    data: tuple["EncryptedPassportElement", ...]
    credentials: "EncryptedCredentials"


class PassportFile(API, frozen=True, kw_only=True):
    file_id: FileId
    file_unique_id: FileUniqueId
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


class EncryptedPassportElement(API, frozen=True, kw_only=True):
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


class EncryptedCredentials(API, frozen=True, kw_only=True):
    data: str
    hash: str
    secret: str


class PassportElementError(
    API,
    frozen=True,
    tag_field="source",
    kw_only=True,
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


class PassportElementErrorDataField(  # noqa: N818 - Telegram API naming
    PassportElementError,
    frozen=True,
    tag="data",
    kw_only=True,
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


class PassportElementErrorFrontSide(  # noqa: N818 - Telegram API naming
    PassportElementError,
    frozen=True,
    tag="front_side",
    kw_only=True,
):
    type: PassportElementFrontSideType
    file_hash: str
    message: str


@unique
class PassportElementReverseSideType(StrEnum):
    DRIVER_LICENSE = PassportElementType.DRIVER_LICENSE
    IDENTITY_CARD = PassportElementType.IDENTITY_CARD


class PassportElementErrorReverseSide(  # noqa: N818 - Telegram API naming
    PassportElementError,
    frozen=True,
    tag="reverse_side",
    kw_only=True,
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


class PassportElementErrorSelfie(  # noqa: N818 - Telegram API naming
    PassportElementError,
    frozen=True,
    tag="selfie",
    kw_only=True,
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


class PassportElementErrorFile(  # noqa: N818 - Telegram API naming
    PassportElementError,
    frozen=True,
    tag="file",
    kw_only=True,
):
    type: PassportElementFileType
    file_hash: str
    message: str


class PassportElementErrorFiles(  # noqa: N818 - Telegram API naming
    PassportElementError,
    frozen=True,
    tag="files",
    kw_only=True,
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


class PassportElementErrorTranslationFile(  # noqa: N818 - Telegram API naming
    PassportElementError,
    frozen=True,
    tag="translation_file",
    kw_only=True,
):
    type: PassportElementTranslationFileType
    file_hash: str
    message: str


class PassportElementErrorTranslationFiles(  # noqa: N818 - Telegram API naming
    PassportElementError,
    frozen=True,
    tag="translation_files",
    kw_only=True,
):
    type: PassportElementTranslationFileType
    file_hashes: Sequence[str]
    message: str


class PassportElementErrorUnspecified(  # noqa: N818 - Telegram API naming
    PassportElementError,
    frozen=True,
    tag="unspecified",
    kw_only=True,
):
    type: PassportElementType
    element_hash: str
    message: str


class Game(API, frozen=True, kw_only=True):
    title: str
    description: str
    photo: tuple[PhotoSize, ...]
    text: str | None = None
    text_entities: tuple[MessageEntity, ...] | None = None
    animation: "Animation | None" = None


class CallbackGame(API, frozen=True, kw_only=True):
    pass


class GameHighScore(API, frozen=True, kw_only=True):
    position: int
    user: User
    score: int
