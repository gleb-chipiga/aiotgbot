import logging
from abc import ABC, abstractmethod
from itertools import count
from typing import Any, Final, Iterable, Sequence, Type, TypeVar

import msgspec

from .api_types import (
    BotCommand,
    BotCommandScope,
    Chat,
    ChatAdministratorRights,
    ChatInviteLink,
    ChatMember,
    ChatPermissions,
    File,
    GameHighScore,
    InlineKeyboardMarkup,
    InlineQueryResult,
    InputFile,
    InputMedia,
    InputSticker,
    LabeledPrice,
    MaskPosition,
    MenuButton,
    Message,
    MessageEntity,
    MessageId,
    PassportElementError,
    Poll,
    ReplyMarkup,
    SentWebAppMessage,
    ShippingOption,
    Sticker,
    StickerSet,
    Update,
    User,
    UserProfilePhotos,
    WebhookInfo,
)
from .constants import (
    ChatAction,
    DiceEmoji,
    ParseMode,
    PollType,
    RequestMethod,
    StickerFormat,
    StickerType,
    UpdateType,
)

__all__ = (
    "ApiMethods",
    "ParamType",
)

api_logger: Final[logging.Logger] = logging.getLogger("aiotgbot.api")


ParamType = int | float | str | InputFile | None


def _encode_json(obj: Any) -> str | None:
    if obj is not None:
        return msgspec.json.encode(obj).decode()
    else:
        return None


T = TypeVar("T")


class ApiMethods(ABC):
    @abstractmethod
    async def _request(
        self,
        http_method: RequestMethod,
        api_method: str,
        type_: Type[T],
        **params: ParamType,
    ) -> T:
        ...

    @abstractmethod
    async def _safe_request(
        self,
        http_method: RequestMethod,
        api_method: str,
        chat_id: int | str,
        type_: Type[T],
        **params: ParamType,
    ) -> T:
        ...

    async def get_updates(
        self,
        offset: int | None = None,
        limit: int | None = None,
        timeout: int | None = None,
        allowed_updates: Sequence[UpdateType] | None = None,
    ) -> tuple[Update, ...]:
        api_logger.debug(
            "Get updates offset: %r, limit: %r, timeout: %r, "
            "allowed_updates: %r",
            offset,
            limit,
            timeout,
            allowed_updates,
        )
        return await self._request(
            RequestMethod.GET,
            "getUpdates",
            tuple[Update, ...],
            offset=offset,
            limit=limit,
            timeout=timeout,
            allowed_updates=_encode_json(allowed_updates),
        )

    async def set_webhook(
        self,
        url: str | None = None,
        certificate: InputFile | None = None,
        ip_address: str | None = None,
        max_connections: int | None = None,
        allowed_updates: Sequence[UpdateType] | None = None,
        drop_pending_updates: bool | None = None,
        secret_token: str | None = None,
    ) -> bool:
        api_logger.debug("Set webhook")
        return await self._request(
            RequestMethod.POST,
            "setWebhook",
            bool,
            url=url,
            certificate=certificate,
            ip_address=ip_address,
            max_connections=max_connections,
            allowed_updates=_encode_json(allowed_updates),
            drop_pending_updates=drop_pending_updates,
            secret_token=secret_token,
        )

    async def delete_webhook(
        self,
        drop_pending_updates: bool | None = None,
    ) -> bool:
        api_logger.debug("Delete webhook")
        return await self._request(
            RequestMethod.POST,
            "deleteWebhook",
            bool,
            drop_pending_updates=drop_pending_updates,
        )

    async def get_webhook_info(
        self,
    ) -> WebhookInfo:
        api_logger.debug("Get webhook info")
        return await self._request(
            RequestMethod.GET,
            "getWebhookInfo",
            WebhookInfo,
        )

    async def get_me(
        self,
    ) -> User:
        api_logger.debug("Get me")
        return await self._request(
            RequestMethod.GET,
            "getMe",
            User,
        )

    async def log_out(
        self,
    ) -> bool:
        api_logger.debug("Log out")
        return await self._request(
            RequestMethod.POST,
            "logOut",
            bool,
        )

    async def close(
        self,
    ) -> bool:
        api_logger.debug("Close")
        return await self._request(
            RequestMethod.POST,
            "close",
            bool,
        )

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        parse_mode: ParseMode | None = None,
        entities: Sequence[MessageEntity] | None = None,
        disable_web_page_preview: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send message %r to chat "%s"',
            text,
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendMessage",
            chat_id,
            Message,
            text=text,
            parse_mode=parse_mode,
            entities=_encode_json(entities),
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def forward_message(
        self,
        chat_id: int | str,
        from_chat_id: int | str,
        message_id: int,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
    ) -> Message:
        api_logger.debug(
            'Forward message %s to "%s" from "%s"',
            message_id,
            chat_id,
            from_chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "forwardMessage",
            chat_id,
            Message,
            from_chat_id=from_chat_id,
            message_id=message_id,
            disable_notification=disable_notification,
            protect_content=protect_content,
        )

    async def copy_message(
        self,
        chat_id: int | str,
        from_chat_id: int | str,
        message_id: int,
        caption: str | None = None,
        parse_mode: ParseMode | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> MessageId:
        api_logger.debug(
            'Copy message %s to "%s" from "%s"',
            message_id,
            chat_id,
            from_chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "copyMessage",
            chat_id,
            MessageId,
            from_chat_id=from_chat_id,
            message_id=message_id,
            parse_mode=parse_mode,
            caption_entities=_encode_json(caption_entities),
            caption=caption,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_photo(
        self,
        chat_id: int | str,
        photo: InputFile | str,
        caption: str | None = None,
        parse_mode: ParseMode | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send photo to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendPhoto",
            chat_id,
            Message,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=_encode_json(caption_entities),
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_audio(
        self,
        chat_id: int | str,
        audio: InputFile | str,
        caption: str | None = None,
        parse_mode: ParseMode | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        duration: int | None = None,
        performer: str | None = None,
        title: str | None = None,
        thumb: InputFile | str | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send audio to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendAudio",
            chat_id,
            Message,
            audio=audio,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=_encode_json(caption_entities),
            disable_notification=disable_notification,
            protect_content=protect_content,
            duration=duration,
            performer=performer,
            title=title,
            thumb=thumb,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_document(
        self,
        chat_id: int | str,
        document: InputFile | str,
        thumb: InputFile | str | None = None,
        caption: str | None = None,
        parse_mode: ParseMode | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        disable_content_type_detection: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        duration: int | None = None,
        performer: str | None = None,
        title: str | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send document to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendDocument",
            chat_id,
            Message,
            document=document,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=_encode_json(caption_entities),
            disable_content_type_detection=disable_content_type_detection,
            disable_notification=disable_notification,
            protect_content=protect_content,
            duration=duration,
            performer=performer,
            title=title,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_video(
        self,
        chat_id: int | str,
        video: InputFile | str,
        duration: int | None = None,
        width: int | None = None,
        height: int | None = None,
        thumb: InputFile | str | None = None,
        caption: str | None = None,
        parse_mode: ParseMode | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        supports_streaming: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send video to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendVideo",
            chat_id,
            Message,
            video=video,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=_encode_json(caption_entities),
            supports_streaming=supports_streaming,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_animation(
        self,
        chat_id: int | str,
        animation: InputFile | str,
        duration: int | None = None,
        width: int | None = None,
        height: int | None = None,
        thumb: InputFile | str | None = None,
        caption: str | None = None,
        parse_mode: ParseMode | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send animation to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendAnimation",
            chat_id,
            Message,
            animation=animation,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=_encode_json(caption_entities),
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_voice(
        self,
        chat_id: int | str,
        voice: InputFile | str,
        caption: str | None = None,
        parse_mode: ParseMode | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        duration: int | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send voice to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendVoice",
            chat_id,
            Message,
            voice=voice,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=_encode_json(caption_entities),
            duration=duration,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_video_note(
        self,
        chat_id: int | str,
        video_note: InputFile | str,
        duration: int | None = None,
        length: int | None = None,
        thumb: InputFile | str | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send video not to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendVideoNote",
            chat_id,
            Message,
            video_note=video_note,
            duration=duration,
            length=length,
            thumb=thumb,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_media_group(
        self,
        chat_id: int | str,
        media: Iterable[InputMedia],
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
    ) -> tuple[Message, ...]:
        api_logger.debug(
            'Send media group to "%s"',
            chat_id,
        )
        attached_media = []
        attachments = {}
        counter = count()
        for item in media:
            if isinstance(item.media, str):
                attached_media.append(item)
            else:
                attachment_name = f"attachment{next(counter)}"
                attachments[attachment_name] = item.media
                attached_media.append(
                    msgspec.structs.replace(
                        item, media=f"attach://{attachment_name}"
                    )
                )
        return await self._safe_request(
            RequestMethod.POST,
            "sendMediaGroup",
            chat_id,
            tuple[Message, ...],
            media=_encode_json(attached_media),
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            **attachments,
        )

    async def send_location(
        self,
        chat_id: int | str,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
        live_period: int | None = None,
        heading: int | None = None,
        proximity_alert_radius: int | None = None,
        length: int | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send location to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendLocation",
            chat_id,
            Message,
            latitude=latitude,
            longitude=longitude,
            horizontal_accuracy=horizontal_accuracy,
            live_period=live_period,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            length=length,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def edit_message_live_location(
        self,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
        heading: int | None = None,
        proximity_alert_radius: int | None = None,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message | bool:
        api_logger.debug(
            'Edit live location %s in "%s"',
            message_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "editMessageLiveLocation",
            Message | bool,  # type: ignore # TODO
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            latitude=latitude,
            longitude=longitude,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            proximity_alert_radius=proximity_alert_radius,
            reply_markup=_encode_json(reply_markup),
        )

    async def stop_message_live_location(
        self,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message | bool:
        api_logger.debug(
            'Stop live location %s in "%s"',
            message_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "stopMessageLiveLocation",
            Message | bool,  # type: ignore # TODO
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_venue(
        self,
        chat_id: int | str,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: str | None = None,
        foursquare_type: str | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send venue to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendVenue",
            chat_id,
            Message,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            foursquare_id=foursquare_id,
            foursquare_type=foursquare_type,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_contact(
        self,
        chat_id: int | str,
        phone_number: str,
        first_name: str,
        last_name: str | None = None,
        vcard: str | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send contact to "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendContact",
            chat_id,
            Message,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            vcard=vcard,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_poll(
        self,
        chat_id: int | str,
        question: str,
        options: Sequence[str],
        is_anonymous: bool | None = None,
        type_: PollType | None = None,
        allows_multiple_answers: bool | None = None,
        correct_option_id: int | None = None,
        is_closed: bool | None = None,
        explanation: str | None = None,
        explanation_parse_mode: ParseMode | None = None,
        explanation_entities: Sequence[MessageEntity] | None = None,
        open_period: int | None = None,
        close_date: int | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send poll to chat "%s"',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendPoll",
            chat_id,
            Message,
            question=question,
            options=_encode_json(options),
            is_anonymous=is_anonymous,
            type=type_,
            allows_multiple_answers=allows_multiple_answers,
            correct_option_id=correct_option_id,
            is_closed=is_closed,
            explanation=explanation,
            explanation_parse_mode=explanation_parse_mode,
            explanation_entities=_encode_json(explanation_entities),
            open_period=open_period,
            close_date=close_date,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_dice(
        self,
        chat_id: int | str,
        emoji: DiceEmoji | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send dice "%s" to chat "%s"',
            emoji,
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendDice",
            chat_id,
            Message,
            emoji=emoji,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def send_chat_action(
        self,
        chat_id: int | str,
        action: ChatAction,
    ) -> bool:
        api_logger.debug(
            'Send action "%s" to chat "%s"',
            action,
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendChatAction",
            chat_id,
            bool,
            action=action.value,
        )

    async def get_user_profile_photos(
        self,
        user_id: int,
        offset: int | None = None,
        limit: int | None = None,
    ) -> UserProfilePhotos:
        api_logger.debug(
            "Get user profile photos %s offset %s limit %s",
            user_id,
            offset,
            limit,
        )
        return await self._request(
            RequestMethod.GET,
            "getUserProfilePhotos",
            UserProfilePhotos,
            user_id=user_id,
            offset=offset,
            limit=limit,
        )

    async def get_file(
        self,
        file_id: str,
    ) -> File:
        api_logger.debug(
            'Get file "%s"',
            file_id,
        )
        return await self._request(
            RequestMethod.GET,
            "getFile",
            File,
            file_id=file_id,
        )

    async def ban_chat_member(
        self,
        chat_id: int | str,
        user_id: int,
        until_date: int | None = None,
        revoke_messages: bool | None = None,
    ) -> bool:
        return await self._request(
            RequestMethod.POST,
            "banChatMember",
            bool,
            chat_id=chat_id,
            user_id=user_id,
            until_date=until_date,
            revoke_messages=revoke_messages,
        )

    async def unban_chat_member(
        self,
        chat_id: int | str,
        user_id: int,
        only_if_banned: bool | None = None,
    ) -> bool:
        api_logger.debug(
            'Unban member %s in "%s"',
            user_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "unbanChatMember",
            bool,
            chat_id=chat_id,
            user_id=user_id,
            only_if_banned=only_if_banned,
        )

    async def restrict_chat_member(
        self,
        chat_id: int | str,
        user_id: int,
        permissions: ChatPermissions,
        until_date: int | None = None,
    ) -> bool:
        api_logger.debug(
            'Restrict member %s in "%s"',
            user_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "restrictChatMember",
            bool,
            chat_id=chat_id,
            user_id=user_id,
            permissions=_encode_json(permissions),
            until_date=until_date,
        )

    async def promote_chat_member(
        self,
        chat_id: int | str,
        user_id: int,
        is_anonymous: int | None = None,
        can_manage_chat: int | None = None,
        can_change_info: int | None = None,
        can_post_messages: bool | None = None,
        can_edit_messages: bool | None = None,
        can_delete_messages: bool | None = None,
        can_manage_video_chats: bool | None = None,
        can_invite_users: bool | None = None,
        can_restrict_members: bool | None = None,
        can_pin_messages: bool | None = None,
        can_promote_members: bool | None = None,
    ) -> bool:
        api_logger.debug(
            'Promote member %s in "%s"',
            user_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "promoteChatMember",
            bool,
            chat_id=chat_id,
            user_id=user_id,
            is_anonymous=is_anonymous,
            can_manage_chat=can_manage_chat,
            can_change_info=can_change_info,
            can_post_messages=can_post_messages,
            can_edit_messages=can_edit_messages,
            can_delete_messages=can_delete_messages,
            can_manage_video_chats=can_manage_video_chats,
            can_invite_users=can_invite_users,
            can_restrict_members=can_restrict_members,
            can_pin_messages=can_pin_messages,
            can_promote_members=can_promote_members,
        )

    async def set_chat_administrator_custom_title(
        self,
        chat_id: int | str,
        user_id: int,
        custom_title: str,
    ) -> bool:
        api_logger.debug(
            'Set title "%s" for admin %s in "%s"',
            custom_title,
            user_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "setChatAdministratorCustomTitle",
            bool,
            chat_id=chat_id,
            user_id=user_id,
            custom_title=custom_title,
        )

    async def ban_chat_sender_chat(
        self,
        chat_id: int | str,
        sender_chat_id: int,
        until_date: int | None,
    ) -> bool:
        api_logger.debug(
            'Ban chat "%s" sender chat "%s"',
            chat_id,
            sender_chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "banChatSenderChat",
            bool,
            chat_id=chat_id,
            sender_chat_id=sender_chat_id,
            until_date=until_date,
        )

    async def unban_chat_sender_chat(
        self,
        chat_id: int | str,
        sender_chat_id: int,
    ) -> bool:
        api_logger.debug(
            'Unban chat "%s" sender chat "%s"',
            chat_id,
            sender_chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "unbanChatSenderChat",
            bool,
            chat_id=chat_id,
            sender_chat_id=sender_chat_id,
        )

    async def export_chat_invite_link(
        self,
        chat_id: int | str,
    ) -> str:
        api_logger.debug(
            'Export chat "%s" invite link',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "exportChatInviteLink",
            str,
            chat_id=chat_id,
        )

    async def create_chat_invite_link(
        self,
        chat_id: int | str,
        name: str | None = None,
        expire_date: int | None = None,
        member_limit: int | None = None,
        creates_join_request: bool | None = None,
    ) -> ChatInviteLink:
        api_logger.debug(
            'Create chat "%s" invite link',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "createChatInviteLink",
            ChatInviteLink,
            chat_id=chat_id,
            name=name,
            expire_date=expire_date,
            member_limit=member_limit,
            creates_join_request=creates_join_request,
        )

    async def edit_chat_invite_link(
        self,
        chat_id: int | str,
        invite_link: str,
        name: str | None = None,
        expire_date: int | None = None,
        member_limit: int | None = None,
        creates_join_request: bool | None = None,
    ) -> ChatInviteLink:
        api_logger.debug(
            'Edit chat "%s" invite link',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "editChatInviteLink",
            ChatInviteLink,
            chat_id=chat_id,
            invite_link=invite_link,
            name=name,
            expire_date=expire_date,
            member_limit=member_limit,
            creates_join_request=creates_join_request,
        )

    async def revoke_chat_invite_link(
        self,
        chat_id: int | str,
        invite_link: str,
    ) -> ChatInviteLink:
        api_logger.debug(
            'Revoke chat "%s" invite link',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "revokeChatInviteLink",
            ChatInviteLink,
            chat_id=chat_id,
            invite_link=invite_link,
        )

    async def approve_chat_join_request(
        self,
        chat_id: int | str,
        user_id: int,
    ) -> bool:
        api_logger.debug(
            'Approve "%s" chat "%s" join request',
            chat_id,
            user_id,
        )
        return await self._request(
            RequestMethod.POST,
            "approveChatJoinRequest",
            bool,
            chat_id=chat_id,
            user_id=user_id,
        )

    async def decline_chat_join_request(
        self,
        chat_id: int | str,
        user_id: int,
    ) -> bool:
        api_logger.debug(
            'Decline "%s" chat "%s" join request',
            chat_id,
            user_id,
        )
        return await self._request(
            RequestMethod.POST,
            "declineChatJoinRequest",
            bool,
            chat_id=chat_id,
            user_id=user_id,
        )

    async def set_chat_permissions(
        self,
        chat_id: int | str,
        permissions: ChatPermissions,
    ) -> bool:
        api_logger.debug(
            'Set chat "%s" permissions',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "setChatPermissions",
            chat_id,
            bool,
            permissions=_encode_json(permissions),
        )

    async def set_chat_photo(
        self,
        chat_id: int | str,
        photo: InputFile,
    ) -> bool:
        api_logger.debug(
            'Set chat "%s" photo',
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "setChatPhoto",
            chat_id,
            bool,
            photo=photo,
        )

    async def delete_chat_photo(
        self,
        chat_id: int | str,
    ) -> bool:
        api_logger.debug(
            'Delete chat "%s" photo',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "deleteChatPhoto",
            bool,
            chat_id=chat_id,
        )

    async def set_chat_title(
        self,
        chat_id: int | str,
        title: str,
    ) -> bool:
        api_logger.debug(
            'Set title "%s" for chat "%s"',
            title,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "setChatTitle",
            bool,
            chat_id=chat_id,
            title=title,
        )

    async def set_chat_description(
        self,
        chat_id: int | str,
        description: str,
    ) -> bool:
        api_logger.debug(
            'Set chat "%s" description',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "setChatDescription",
            bool,
            chat_id=chat_id,
            description=description,
        )

    async def pin_chat_message(
        self,
        chat_id: int | str,
        message_id: int,
        disable_notification: bool | None = None,
    ) -> bool:
        api_logger.debug(
            'Pin message %s in chat "%s"',
            message_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "pinChatMessage",
            bool,
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=disable_notification,
        )

    async def unpin_chat_message(
        self,
        chat_id: int | str,
        message_id: int | None,
    ) -> bool:
        api_logger.debug(
            'Unpin message "%s" in chat "%s"',
            message_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "unpinChatMessage",
            bool,
            chat_id=chat_id,
            message_id=message_id,
        )

    async def unpin_all_chat_messages(
        self,
        chat_id: int | str,
    ) -> bool:
        api_logger.debug(
            'Unpin all messages in chat "%s"',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "unpinAllChatMessages",
            bool,
            chat_id=chat_id,
        )

    async def leave_chat(
        self,
        chat_id: int | str,
    ) -> bool:
        api_logger.debug(
            'Leave chat "%s"',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "leaveChat",
            bool,
            chat_id=chat_id,
        )

    async def get_chat(
        self,
        chat_id: int | str,
    ) -> Chat:
        api_logger.debug(
            'Get chat "%s"',
            chat_id,
        )
        return await self._request(
            RequestMethod.GET,
            "getChat",
            Chat,
            chat_id=chat_id,
        )

    async def get_chat_administrators(
        self,
        chat_id: int | str,
    ) -> tuple[ChatMember, ...]:
        api_logger.debug(
            'Get chat administrators "%s"',
            chat_id,
        )
        return await self._request(
            RequestMethod.GET,
            "getChatAdministrators",
            tuple[ChatMember, ...],
            chat_id=chat_id,
        )

    async def get_chat_member_count(
        self,
        chat_id: int | str,
    ) -> int:
        api_logger.debug(
            'Get chat member count "%s"',
            chat_id,
        )
        return await self._request(
            RequestMethod.GET,
            "getChatMemberCount",
            int,
            chat_id=chat_id,
        )

    async def get_chat_member(
        self, chat_id: int | str, user_id: int
    ) -> ChatMember:
        api_logger.debug(
            'Get chat "%s" member %s',
            chat_id,
            user_id,
        )
        return await self._request(
            RequestMethod.GET,
            "getChatMember",
            ChatMember,
            chat_id=chat_id,
            user_id=user_id,
        )

    async def set_chat_sticker_set(
        self,
        chat_id: int | str,
        sticker_set_name: str,
    ) -> bool:
        api_logger.debug(
            'Set chat "%s" sticker set "%s"',
            chat_id,
            sticker_set_name,
        )
        return await self._request(
            RequestMethod.POST,
            "setChatStickerSet",
            bool,
            chat_id=chat_id,
            sticker_set_name=sticker_set_name,
        )

    async def delete_chat_sticker_set(
        self,
        chat_id: int | str,
    ) -> bool:
        api_logger.debug(
            'Delete chat "%s" sticker set',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "deleteChatStickerSet",
            bool,
            chat_id=chat_id,
        )

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: str | None = None,
        show_alert: bool | None = None,
        url: str | None = None,
        cache_time: int | None = None,
    ) -> bool:
        api_logger.debug(
            'Answer callback query "%s"',
            callback_query_id,
        )
        return await self._request(
            RequestMethod.POST,
            "answerCallbackQuery",
            bool,
            callback_query_id=callback_query_id,
            text=text,
            show_alert=show_alert,
            url=url,
            cache_time=cache_time,
        )

    async def set_my_commands(
        self,
        commands: Sequence[BotCommand],
        scope: BotCommandScope | None = None,
        language_code: str | None = None,
    ) -> bool:
        api_logger.debug(
            'Set my commands "%s"',
            commands,
        )
        return await self._request(
            RequestMethod.POST,
            "setMyCommands",
            bool,
            commands=_encode_json(commands),
            scope=_encode_json(scope),
            language_code=language_code,
        )

    async def set_chat_menu_button(
        self,
        chat_id: int | None,
        menu_button: MenuButton | None,
    ) -> bool:
        api_logger.debug(
            'Set chat menu button "%r"',
            menu_button,
        )
        return await self._request(
            RequestMethod.POST,
            "setChatMenuButton",
            bool,
            chat_id=chat_id,
            menu_button=_encode_json(menu_button),
        )

    async def get_chat_menu_button(
        self,
        chat_id: int | None,
    ) -> MenuButton:
        api_logger.debug(
            'Get chat menu button "%r"',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "getChatMenuButton",
            MenuButton,
            chat_id=chat_id,
        )

    async def set_my_default_administrator_rights(
        self,
        rights: ChatAdministratorRights | None,
        for_channels: bool | None,
    ) -> bool:
        api_logger.debug(
            "Set my default administrator rights %r",
            rights,
        )
        return await self._request(
            RequestMethod.POST,
            "setMyDefaultAdministratorRights",
            bool,
            rights=_encode_json(rights),
            for_channels=for_channels,
        )

    async def get_my_default_administrator_rights(
        self,
        for_channels: bool | None,
    ) -> ChatAdministratorRights:
        api_logger.debug(
            "Get my default administrator rights",
        )
        return await self._request(
            RequestMethod.POST,
            "getMyDefaultAdministratorRights",
            ChatAdministratorRights,
            for_channels=for_channels,
        )

    async def get_my_commands(
        self,
        scope: BotCommandScope | None = None,
        language_code: str | None = None,
    ) -> tuple[BotCommand, ...]:
        api_logger.debug(
            "Get my commands",
        )
        return await self._request(
            RequestMethod.GET,
            "getMyCommands",
            tuple[BotCommand, ...],
            scope=_encode_json(scope),
            language_code=language_code,
        )

    async def delete_my_commands(
        self,
        scope: BotCommandScope | None = None,
        language_code: str | None = None,
    ) -> bool:
        api_logger.debug(
            "Delete my commands",
        )
        return await self._request(
            RequestMethod.GET,
            "deleteMyCommands",
            bool,
            scope=_encode_json(scope),
            language_code=language_code,
        )

    async def edit_message_text(
        self,
        text: str,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
        parse_mode: ParseMode | None = None,
        entities: Sequence[MessageEntity] | None = None,
        disable_web_page_preview: bool | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message | bool:
        if (
            chat_id is None or message_id is None
        ) and inline_message_id is None:
            raise RuntimeError(
                "chat_id or message_id and inline_message_id is None"
            )
        if inline_message_id is None:
            api_logger.debug(
                'Edit message %s in "%s" text',
                message_id,
                chat_id,
            )
        else:
            api_logger.debug(
                'Edit inline message "%s" text',
                inline_message_id,
            )
        return await self._request(
            RequestMethod.POST,
            "editMessageText",
            Message | bool,  # type: ignore # TODO
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            text=text,
            parse_mode=parse_mode,
            entities=_encode_json(entities),
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=_encode_json(reply_markup),
        )

    async def edit_message_caption(
        self,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
        caption: str | None = None,
        parse_mode: ParseMode | None = None,
        caption_entities: Sequence[MessageEntity] | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message | bool:
        if (
            chat_id is None or message_id is None
        ) and inline_message_id is None:
            raise RuntimeError(
                "chat_id or message_id and inline_message_id is None"
            )
        if inline_message_id is None:
            api_logger.debug(
                'Edit message %s in "%s" caption',
                message_id,
                chat_id,
            )
        else:
            api_logger.debug(
                'Edit inline message "%s" caption',
                inline_message_id,
            )
        return await self._request(
            RequestMethod.POST,
            "editMessageCaption",
            Message | bool,  # type: ignore # TODO
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=_encode_json(caption_entities),
            reply_markup=_encode_json(reply_markup),
        )

    async def edit_message_media(
        self,
        media: InputMedia,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message | bool:
        if (
            chat_id is None or message_id is None
        ) and inline_message_id is None:
            raise RuntimeError(
                "chat_id or message_id and inline_message_id is None"
            )
        if inline_message_id is None:
            api_logger.debug(
                'Edit message %s in "%s" media',
                message_id,
                chat_id,
            )
        else:
            api_logger.debug(
                'Edit inline message "%s" media',
                inline_message_id,
            )
        attachments = {}
        if not isinstance(media.media, str):
            attachment_name = "attachment0"
            attachments[attachment_name] = media.media
            media = msgspec.structs.replace(
                media, media=f"attach://{attachment_name}"
            )
        return await self._request(
            RequestMethod.POST,
            "editMessageMedia",
            Message | bool,  # type: ignore # TODO
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            media=_encode_json(media),
            reply_markup=_encode_json(reply_markup),
            **attachments,
        )

    async def edit_message_reply_markup(
        self,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message | bool:
        if (
            chat_id is None or message_id is None
        ) and inline_message_id is None:
            raise RuntimeError(
                "chat_id or message_id and inline_message_id is None"
            )
        if inline_message_id is None:
            api_logger.debug(
                'Edit message %s in "%s" reply markup',
                message_id,
                chat_id,
            )
        else:
            api_logger.debug(
                'Edit inline message "%s" reply markup',
                inline_message_id,
            )
        return await self._request(
            RequestMethod.POST,
            "editMessageReplyMarkup",
            Message | bool,  # type: ignore # TODO
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
            reply_markup=_encode_json(reply_markup),
        )

    async def stop_poll(
        self,
        chat_id: int | str,
        message_id: int,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Poll:
        api_logger.debug(
            'Stop poll %s in "%s"',
            message_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "stopPoll",
            Poll,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=_encode_json(reply_markup),
        )

    async def delete_message(
        self,
        chat_id: int | str | None = None,
        message_id: int | None = None,
    ) -> bool:
        api_logger.debug(
            'Delete message %s in "%s"',
            message_id,
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "deleteMessage",
            bool,
            chat_id=chat_id,
            message_id=message_id,
        )

    async def send_sticker(
        self,
        chat_id: int | str,
        sticker: InputFile | str,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: ReplyMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send sticker to "%s"',
            chat_id,
        )
        return await self._request(
            RequestMethod.POST,
            "sendSticker",
            Message,
            chat_id=chat_id,
            sticker=sticker,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def get_sticker_set(
        self,
        name: str,
    ) -> StickerSet:
        api_logger.debug(
            'Get sticker set "%s"',
            name,
        )
        return await self._request(
            RequestMethod.GET,
            "getStickerSet",
            StickerSet,
            name=name,
        )

    async def get_custom_emoji_stickers(
        self,
        custom_emoji_ids: Sequence[str],
    ) -> tuple[Sticker, ...]:
        api_logger.debug("Get custom emoji stickers")
        return await self._request(
            RequestMethod.GET,
            "getCustomEmojiStickers",
            tuple[Sticker, ...],
            custom_emoji_ids=_encode_json(custom_emoji_ids),
        )

    async def upload_sticker_file(
        self,
        user_id: int,
        png_sticker: InputFile,
    ) -> File:
        api_logger.debug(
            "Upload sticker file for %s",
            user_id,
        )
        return await self._request(
            RequestMethod.POST,
            "uploadStickerFile",
            File,
            user_id=user_id,
            png_sticker=png_sticker,
        )

    async def create_new_sticker_set(
        self,
        user_id: int,
        name: str,
        title: str,
        emojis: str,
        stickers: Iterable[InputSticker],
        sticker_format: StickerFormat,
        sticker_type: StickerType | None = None,
        needs_repainting: bool | None = None,
    ) -> bool:
        api_logger.debug(
            'Create new sticker set "%s" for %s',
            name,
            user_id,
        )
        attached_media = []
        attachments = {}
        counter = count()
        for sticker in stickers:
            if isinstance(sticker.sticker, str):
                attached_media.append(sticker)
            else:
                attachment_name = f"attachment{next(counter)}"
                attachments[attachment_name] = sticker.sticker
                attached_media.append(
                    msgspec.structs.replace(
                        sticker, sticker=f"attach://{attachment_name}"
                    )
                )
        return await self._request(
            RequestMethod.POST,
            "createNewStickerSet",
            bool,
            user_id=user_id,
            name=name,
            title=title,
            emojis=emojis,
            stickers=_encode_json(attached_media),
            sticker_format=sticker_format,
            sticker_type=sticker_type,
            needs_repainting=needs_repainting,
        )

    async def add_sticker_to_set(
        self,
        user_id: int,
        name: str,
        title: str,
        emojis: str,
        png_sticker: InputFile | str,
        tgs_sticker: InputFile | None = None,
        webm_sticker: InputFile | None = None,
        mask_position: MaskPosition | None = None,
    ) -> File:
        api_logger.debug(
            'Add sticker to set "%s" for %s',
            name,
            user_id,
        )
        return await self._request(
            RequestMethod.POST,
            "addStickerToSet",
            File,
            user_id=user_id,
            name=name,
            title=title,
            emojis=emojis,
            png_sticker=png_sticker,
            tgs_sticker=tgs_sticker,
            webm_sticker=webm_sticker,
            mask_position=_encode_json(mask_position),
        )

    async def set_sticker_position_in_set(
        self,
        sticker: str,
        position: int,
    ) -> bool:
        api_logger.debug(
            'Set sticker "%s" position to %s',
            sticker,
            position,
        )
        return await self._request(
            RequestMethod.POST,
            "setStickerPositionInSet",
            bool,
            sticker=sticker,
            position=position,
        )

    async def delete_sticker_from_set(
        self,
        sticker: str,
    ) -> bool:
        api_logger.debug(
            'Delete sticker "%s" from set',
            sticker,
        )
        return await self._request(
            RequestMethod.POST,
            "deleteStickerFromSet",
            bool,
            sticker=sticker,
        )

    async def set_sticker_set_thumb(
        self,
        name: str,
        user_id: int,
        thumb: InputFile | str | None = None,
    ) -> bool:
        api_logger.debug(
            'Set sticker set "%s" owned by "%s" thumb',
            name,
            user_id,
        )
        return await self._request(
            RequestMethod.POST,
            "setStickerSetThumb",
            bool,
            name=name,
            user_id=user_id,
            thumb=thumb,
        )

    async def answer_inline_query(
        self,
        inline_query_id: str,
        results: Sequence[InlineQueryResult],
        cache_time: int | None = None,
        is_personal: bool | None = None,
        next_offset: str | None = None,
        switch_pm_text: str | None = None,
        switch_pm_parameter: str | None = None,
    ) -> bool:
        api_logger.debug(
            'Answer inline query "%s"',
            inline_query_id,
        )
        return await self._request(
            RequestMethod.POST,
            "answerInlineQuery",
            bool,
            inline_query_id=inline_query_id,
            results=_encode_json(results),
            cache_time=cache_time,
            is_personal=is_personal,
            next_offset=next_offset,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter=switch_pm_parameter,
        )

    async def answer_web_app_query(
        self,
        web_app_query_id: str,
        results: Sequence[InlineQueryResult],
    ) -> SentWebAppMessage:
        api_logger.debug(
            'Answer web app query "%s"',
            web_app_query_id,
        )
        return await self._request(
            RequestMethod.POST,
            "answerWebAppQuery",
            SentWebAppMessage,
            web_app_query_id=web_app_query_id,
            results=_encode_json(results),
        )

    async def send_invoice(
        self,
        chat_id: int,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: Sequence[LabeledPrice],
        max_tip_amount: int | None = None,
        suggested_tip_amounts: tuple[int, ...] | None = None,
        start_parameter: str | None = None,
        provider_data: str | None = None,
        photo_url: str | None = None,
        photo_size: int | None = None,
        photo_width: int | None = None,
        photo_height: int | None = None,
        need_name: bool | None = None,
        need_phone_number: bool | None = None,
        need_email: bool | None = None,
        need_shipping_address: bool | None = None,
        send_phone_number_to_provider: bool | None = None,
        send_email_to_provider: bool | None = None,
        is_flexible: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            "Send invoice to %s",
            chat_id,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendInvoice",
            chat_id,
            Message,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=_encode_json(prices),
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=_encode_json(suggested_tip_amounts),
            start_parameter=start_parameter,
            provider_data=provider_data,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            is_flexible=is_flexible,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def create_invoice_link(
        self,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: Sequence[LabeledPrice],
        max_tip_amount: int | None = None,
        suggested_tip_amounts: tuple[int, ...] | None = None,
        start_parameter: str | None = None,
        provider_data: str | None = None,
        photo_url: str | None = None,
        photo_size: int | None = None,
        photo_width: int | None = None,
        photo_height: int | None = None,
        need_name: bool | None = None,
        need_phone_number: bool | None = None,
        need_email: bool | None = None,
        need_shipping_address: bool | None = None,
        send_phone_number_to_provider: bool | None = None,
        send_email_to_provider: bool | None = None,
        is_flexible: bool | None = None,
    ) -> str:
        api_logger.debug(
            "Create invoice link",
        )
        return await self._request(
            RequestMethod.POST,
            "createInvoiceLink",
            str,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=_encode_json(prices),
            max_tip_amount=max_tip_amount,
            suggested_tip_amounts=_encode_json(suggested_tip_amounts),
            start_parameter=start_parameter,
            provider_data=provider_data,
            photo_url=photo_url,
            photo_size=photo_size,
            photo_width=photo_width,
            photo_height=photo_height,
            need_name=need_name,
            need_phone_number=need_phone_number,
            need_email=need_email,
            need_shipping_address=need_shipping_address,
            send_phone_number_to_provider=send_phone_number_to_provider,
            send_email_to_provider=send_email_to_provider,
            is_flexible=is_flexible,
        )

    async def answer_shipping_query(
        self,
        inline_query_id: str,
        ok: bool,
        shipping_options: Sequence[ShippingOption] | None = None,
        error_message: str | None = None,
    ) -> bool:
        api_logger.debug(
            'Answer shipping query "%s"',
            inline_query_id,
        )
        return await self._request(
            RequestMethod.POST,
            "answerShippingQuery",
            bool,
            inline_query_id=inline_query_id,
            ok=ok,
            shipping_options=_encode_json(shipping_options),
            error_message=error_message,
        )

    async def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: str | None = None,
    ) -> bool:
        api_logger.debug(
            'Answer pre checkout query "%s"',
            pre_checkout_query_id,
        )
        return await self._request(
            RequestMethod.POST,
            "answerPreCheckoutQuery",
            bool,
            pre_checkout_query_id=pre_checkout_query_id,
            ok=ok,
            error_message=error_message,
        )

    async def set_passport_data_errors(
        self,
        user_id: int,
        errors: Sequence[PassportElementError],
    ) -> bool:
        api_logger.debug(
            "Set passport data errors %s",
            user_id,
        )
        return await self._request(
            RequestMethod.POST,
            "setPassportDataErrors",
            bool,
            user_id=user_id,
            errors=_encode_json(errors),
        )

    async def send_game(
        self,
        chat_id: int,
        game_short_name: str,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_to_message_id: int | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message:
        api_logger.debug(
            'Send game "%s" to %s',
            chat_id,
            game_short_name,
        )
        return await self._safe_request(
            RequestMethod.POST,
            "sendGame",
            chat_id,
            Message,
            game_short_name=game_short_name,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=_encode_json(reply_markup),
        )

    async def set_game_score(
        self,
        user_id: int,
        score: int,
        force: bool | None = None,
        disable_edit_message: bool | None = None,
        chat_id: int | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
    ) -> Message | bool:
        api_logger.debug(
            "Set game score %s for %s",
            score,
            user_id,
        )
        return await self._request(
            RequestMethod.POST,
            "setGameScore",
            Message | bool,  # type: ignore # TODO
            user_id=user_id,
            score=score,
            force=force,
            disable_edit_message=disable_edit_message,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )

    async def get_game_high_scores(
        self,
        user_id: int,
        chat_id: int | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
    ) -> tuple[GameHighScore, ...]:
        api_logger.debug(
            "Get game high scores for %s",
            user_id,
        )
        return await self._request(
            RequestMethod.POST,
            "getGameHighScores",
            tuple[GameHighScore, ...],
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )
