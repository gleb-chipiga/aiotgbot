import logging
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional, Tuple, Union

from .api_types import (APIResponse, BaseTelegram, Chat, ChatMember, File,
                        GameHighScore, InlineKeyboardMarkup, InlineQueryResult,
                        InputFile, InputMedia, InputMediaPhoto,
                        InputMediaVideo, LabeledPrice, MaskPosition, Message,
                        PassportElementError, Poll, ReplyMarkup,
                        ShippingOption, StickerSet, Update, User,
                        UserProfilePhotos, WebhookInfo)
from .constants import ChatAction, ParseMode, RequestMethod
from .utils import json_dumps

api_logger = logging.getLogger('aiotgbot.api')


def _to_json(value: Optional[BaseTelegram]) -> Optional[str]:
    return json_dumps(value.to_dict()) if value is not None else None


def _strs_to_json(value: Optional[Iterable[str]]) -> Optional[str]:
    return json_dumps(tuple(value)) if value is not None else None


def _parse_mode_to_str(parse_mode: Optional[ParseMode]) -> Optional[str]:
    return parse_mode.value if parse_mode is not None else None


ParamsType = Dict[str, Union[int, float, str, InputFile, InputMedia,
                             Iterable[str],
                             Dict[str, InputFile],
                             Iterable[LabeledPrice],
                             Iterable[ShippingOption],
                             Iterable[InlineQueryResult],
                             Iterable[PassportElementError], None]]


class ApiMethods(ABC):

    @abstractmethod
    async def _request(self, http_method: RequestMethod, api_method: str,
                       params: Optional[ParamsType] = None) -> APIResponse: ...

    @abstractmethod
    async def _safe_request(
            self, http_method: RequestMethod, api_method: str,
            chat_id: Union[int, str],
            params: Optional[ParamsType] = None
    ) -> APIResponse: ...

    async def get_updates(
        self, offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
        allowed_updates: Optional[Iterable[str]] = None
    ) -> Tuple[Update, ...]:
        api_logger.debug(f'Get updates offset: {offset}, limit: {limit}, '
                         f'timeout: {timeout}, '
                         f'allowed_updates: {allowed_updates}')
        response = await self._request(
            RequestMethod.GET, 'getUpdates', params={
                'offset': offset, 'limit': limit, 'timeout': timeout,
                'allowed_updates': _strs_to_json(allowed_updates)})

        return tuple(Update.from_dict(item) for item in response.result)

    async def set_webhook(
        self, url: Optional[str] = None,
        certificate: Optional[InputFile] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[Iterable[str]] = None
    ) -> bool:
        api_logger.debug('Set webhook')
        response = await self._request(
            RequestMethod.POST, 'setWebhook', params={
                'url': url, 'certificate': certificate,
                'max_connections': max_connections,
                'allowed_updates': _strs_to_json(allowed_updates)})

        return response.result

    async def delete_webhook(self) -> bool:
        api_logger.debug('Delete webhook')
        response = await self._request(RequestMethod.POST, 'deleteWebhook')
        return response.result

    async def get_webhook_info(self) -> WebhookInfo:
        api_logger.debug('Get webhook info')
        response = await self._request(RequestMethod.GET, 'getWebhookInfo')

        return WebhookInfo.from_dict(response.result)

    async def get_me(self) -> User:
        api_logger.debug('Get me')
        response = await self._request(RequestMethod.GET, 'getMe')
        return User.from_dict(response.result)

    async def send_message(
        self, chat_id: Union[int, str], text: str,
        parse_mode: Optional[ParseMode] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        api_logger.debug('Send message "%s" to chat %s', text, chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendMessage', chat_id, params={
                'text': text,
                'parse_mode': _parse_mode_to_str(parse_mode),
                'disable_web_page_preview': disable_web_page_preview,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def forward_message(
        self, chat_id: Union[int, str], from_chat_id: Union[int, str],
        message_id: int, disable_notification: Optional[bool] = None
    ) -> Message:
        api_logger.debug('Forward message %s to %s from %s', message_id,
                         chat_id, from_chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'forwardMessage', chat_id, params={
                'from_chat_id': from_chat_id, 'message_id': message_id,
                'disable_notification': disable_notification})

        return Message.from_dict(response.result)

    async def send_photo(
        self, chat_id: Union[int, str],
        photo: Union[InputFile, str],
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendPhoto', chat_id, params={
                'photo': photo, 'caption': caption,
                'parse_mode': _parse_mode_to_str(parse_mode),
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def send_audio(
        self, chat_id: Union[int, str],
        audio: Union[InputFile, str],
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        disable_notification: Optional[bool] = None,
        duration: Optional[int] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        thumb: Optional[Union[InputFile, str]] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendAudio', chat_id, params={
                'audio': audio, 'caption': caption,
                'parse_mode': _parse_mode_to_str(parse_mode),
                'disable_notification': disable_notification,
                'duration': duration, 'performer': performer,
                'title': title, 'thumb': thumb,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def send_document(
        self, chat_id: Union[int, str],
        document: Union[InputFile, str],
        thumb: Optional[Union[InputFile, str]],
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        disable_notification: Optional[bool] = None,
        duration: Optional[int] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendDocument', chat_id, params={
                'document': document, 'thumb': thumb, 'caption': caption,
                'parse_mode': _parse_mode_to_str(parse_mode),
                'disable_notification': disable_notification,
                'duration': duration, 'performer': performer, 'title': title,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def send_video(
        self, chat_id: Union[int, str],
        video: Union[InputFile, str],
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        thumb: Optional[Union[InputFile, str]] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        supports_streaming: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendVideo', chat_id, params={
                'video': video, 'duration': duration, 'width': width,
                'height': height, 'thumb': thumb, 'caption': caption,
                'parse_mode': _parse_mode_to_str(parse_mode),
                'supports_streaming': supports_streaming,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def send_animation(
        self, chat_id: Union[int, str],
        animation: Union[InputFile, str],
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        thumb: Optional[Union[InputFile, str]] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendAnimation', chat_id, params={
                'animation': animation, 'duration': duration, 'width': width,
                'height': height, 'thumb': thumb, 'caption': caption,
                'parse_mode': _parse_mode_to_str(parse_mode),
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def send_voice(
        self, chat_id: Union[int, str],
        voice: Union[InputFile, str],
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        duration: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendVoice', chat_id, params={
                'voice': voice, 'caption': caption,
                'parse_mode': _parse_mode_to_str(parse_mode),
                'duration': duration,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def send_video_note(
        self, chat_id: Union[int, str],
        video_note: Union[InputFile, str],
        duration: Optional[int] = None,
        length: Optional[int] = None,
        thumb: Optional[Union[InputFile, str]] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
             RequestMethod.POST, 'sendVideoNote', chat_id, params={
                'video_note': video_note, 'duration': duration,
                'length': length, 'thumb': thumb,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def send_media_group(
        self, chat_id: Union[int, str],
        media: Iterable[Union[InputMediaPhoto, InputMediaVideo]],
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        attachments: Optional[Dict[str, InputFile]] = None
    ) -> Tuple[Message, ...]:
        params: ParamsType = {
            'media': json_dumps(tuple(item.to_dict() for item in media)),
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id
        }
        if attachments is not None:
            params.update(attachments)
        response = await self._safe_request(
            RequestMethod.POST, 'sendMediaGroup', chat_id, params=params)

        return tuple(Message.from_dict(item) for item in response.result)

    async def send_location(
        self, chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        live_period: Optional[int] = None,
        length: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'editMessageLiveLocation', chat_id, params={
                'latitude': latitude, 'longitude': longitude,
                'live_period': live_period, 'length': length,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def edit_message_live_location(
        self,
        latitude: float,
        longitude: float,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Union[Message, bool]:
        response = await self._request(
            RequestMethod.POST, 'editMessageLiveLocation', params={
                'chat_id': chat_id, 'message_id': message_id,
                'inline_message_id': inline_message_id,
                'latitude': latitude, 'longitude': longitude,
                'reply_markup': _to_json(reply_markup)})

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def stop_message_live_location(
        self, chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Union[Message, bool]:
        response = await self._request(
            RequestMethod.POST, 'stopMessageLiveLocation', params={
                'chat_id': chat_id, 'message_id': message_id,
                'inline_message_id': inline_message_id,
                'reply_markup': _to_json(reply_markup)})

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def send_venue(
        self, chat_id: Union[int, str],
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: Optional[str] = None,
        foursquare_type: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendVenue', chat_id, params={
                'latitude': latitude, 'longitude': longitude, 'title': title,
                'address': address, 'foursquare_id': foursquare_id,
                'foursquare_type': foursquare_type,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def send_contact(
        self, chat_id: Union[int, str],
        phone_number: str,
        first_name: str,
        last_name: Optional[str] = None,
        vcard: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendContact', chat_id, params={
                'phone_number': phone_number, 'first_name': first_name,
                'last_name': last_name, 'vcard': vcard,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def send_poll(self, chat_id: Union[int, str], question: str,
                        options: Iterable[str],
                        disable_notification: Optional[bool] = None,
                        reply_to_message_id: Optional[int] = None,
                        reply_markup: Optional[ReplyMarkup] = None) -> Message:
        api_logger.debug('Send poll "%s" to chat %s', question, chat_id)
        response = await self._safe_request(
            RequestMethod.POST, 'sendPoll', chat_id, params={
                'question': question, 'options': options,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return response.result

    async def send_chat_action(self, chat_id: Union[int, str],
                               action: ChatAction) -> bool:
        api_logger.debug('Send action "%s" to chat %s', action, chat_id)
        response = await self._safe_request(RequestMethod.POST,
                                            'sendChatAction', chat_id,
                                            params={'action': action.value})

        return response.result

    async def get_user_profile_photos(
        self, user_id: int,
        offset: Optional[int] = None,
        limit: Optional[int] = None
    ) -> UserProfilePhotos:
        response = await self._request(RequestMethod.GET,
                                       'getUserProfilePhotos', params={
                                           'user_id': user_id,
                                           'offset': offset, 'limit': limit})

        return UserProfilePhotos.from_dict(response.result)

    async def get_file(self, file_id: str) -> File:
        api_logger.debug('Get file "%s"', file_id)
        response = await self._request(RequestMethod.GET, 'getFile',
                                       params={'file_id': file_id})
        return File.from_dict(response.result)

    async def kick_chat_member(self, chat_id: Union[int, str], user_id: int,
                               until_date: Optional[int] = None) -> bool:
        response = await self._request(RequestMethod.POST, 'kickChatMember',
                                       params={'chat_id': chat_id,
                                               'user_id': user_id,
                                               'until_date': until_date})

        return response.result

    async def unban_chat_member(self, chat_id: Union[int, str],
                                user_id: int) -> bool:
        response = await self._request(RequestMethod.POST, 'unbanChatMember',
                                       params={'chat_id': chat_id,
                                               'user_id': user_id})

        return response.result

    async def restrict_chat_member(
        self, chat_id: Union[int, str],
        user_id: int,
        until_date: Optional[int] = None,
        can_send_messages: Optional[bool] = None,
        can_send_media_messages: Optional[bool] = None,
        can_send_other_messages: Optional[bool] = None,
        can_add_web_page_previews: Optional[bool] = None
    ) -> bool:
        response = await self._request(
            RequestMethod.POST, 'restrictChatMember', params={
                'chat_id': chat_id, 'user_id': user_id,
                'until_date': until_date,
                'can_send_messages': can_send_messages,
                'can_send_media_messages': can_send_media_messages,
                'can_send_other_messages': can_send_other_messages,
                'can_add_web_page_previews': can_add_web_page_previews})

        return response.result

    async def promote_chat_member(
        self, chat_id: Union[int, str],
        user_id: int,
        can_change_info: Optional[int] = None,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_promote_members: Optional[bool] = None
    ) -> bool:
        response = await self._request(
            RequestMethod.POST, 'promoteChatMember', params={
                'chat_id': chat_id, 'user_id': user_id,
                'can_change_info': can_change_info,
                'can_post_messages': can_post_messages,
                'can_edit_messages': can_edit_messages,
                'can_delete_messages': can_delete_messages,
                'can_invite_users': can_invite_users,
                'can_restrict_members': can_restrict_members,
                'can_pin_messages': can_pin_messages,
                'can_promote_members': can_promote_members})

        return response.result

    async def export_chat_invite_link(self, chat_id: Union[int, str]) -> str:
        response = await self._request(RequestMethod.POST,
                                       'exportChatInviteLink',
                                       params={'chat_id': chat_id})

        return response.result

    async def set_chat_photo(
        self, chat_id: Union[int, str],
        photo: InputFile
    ) -> bool:
        response = await self._safe_request(RequestMethod.POST, 'setChatPhoto',
                                            chat_id, params={'photo': photo})

        return response.result

    async def delete_chat_photo(self, chat_id: Union[int, str]) -> bool:
        response = await self._request(RequestMethod.POST, 'deleteChatPhoto',
                                       params={'chat_id': chat_id})

        return response.result

    async def set_chat_title(self, chat_id: Union[int, str],
                             title: str) -> bool:
        response = await self._request(RequestMethod.POST, 'setChatTitle',
                                       params={'chat_id': chat_id,
                                               'title': title})

        return response.result

    async def set_chat_description(self, chat_id: Union[int, str],
                                   description: str) -> bool:
        response = await self._request(
            RequestMethod.POST, 'setChatDescription', params={
                'chat_id': chat_id, 'description': description})

        return response.result

    async def pin_chat_message(
        self, chat_id: Union[int, str], message_id: int,
        disable_notification: Optional[bool] = None
    ) -> bool:
        response = await self._request(
            RequestMethod.POST, 'pinChatMessage', params={
                'chat_id': chat_id, 'message_id': message_id,
                'disable_notification': disable_notification})

        return response.result

    async def unpin_chat_message(self, chat_id: Union[int, str]) -> bool:
        response = await self._request(RequestMethod.POST, 'unpinChatMessage',
                                       params={'chat_id': chat_id})

        return response.result

    async def leave_chat(self, chat_id: Union[int, str]) -> bool:
        api_logger.debug('Leave chat %s', chat_id)
        response = await self._request(RequestMethod.POST, 'leaveChat',
                                       params={'chat_id': chat_id})

        return response.result

    async def get_chat(self, chat_id: Union[int, str]) -> Chat:
        api_logger.debug('Get chat "%s"', chat_id)
        response = await self._request(RequestMethod.GET, 'getChat',
                                       params={'chat_id': chat_id})
        return Chat.from_dict(response.result)

    async def get_chat_administrators(
        self, chat_id: Union[int, str]
    ) -> Tuple[ChatMember, ...]:
        response = await self._request(RequestMethod.GET,
                                       'getChatAdministrators',
                                       params={'chat_id': chat_id})

        return tuple(ChatMember.from_dict(item) for item in response.result)

    async def get_chat_members_count(self, chat_id: Union[int, str]) -> int:
        response = await self._request(
            RequestMethod.GET, 'getChatMembersCount',
            params={'chat_id': chat_id})

        return response.result

    async def get_chat_member(self, chat_id: Union[int, str],
                              user_id: int) -> ChatMember:
        response = await self._request(RequestMethod.GET, 'getChatMember',
                                       params={'chat_id': chat_id,
                                               'user_id': user_id})

        return ChatMember.from_dict(response.result)

    async def set_chat_sticker_set(self, chat_id: Union[int, str],
                                   sticker_set_name: str) -> bool:
        response = await self._request(
            RequestMethod.POST, 'setChatStickerSet', params={
                'chat_id': chat_id, 'sticker_set_name': sticker_set_name})

        return response.result

    async def delete_chat_sticker_set(self, chat_id: Union[int, str]) -> bool:
        response = await self._request(RequestMethod.POST,
                                       'deleteChatStickerSet',
                                       params={'chat_id': chat_id})

        return response.result

    async def answer_callback_query(self, callback_query_id: str,
                                    text: Optional[str] = None,
                                    show_alert: Optional[bool] = None,
                                    url: Optional[str] = None,
                                    cache_time: Optional[int] = None) -> bool:
        response = await self._request(
            RequestMethod.POST, 'answerCallbackQuery', params={
                'callback_query_id': callback_query_id, 'text': text,
                'show_alert': show_alert, 'url': url,
                'cache_time': cache_time})

        return response.result

    async def edit_message_text(
        self,
        text: str,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        disable_web_page_preview: Optional[bool] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Union[Message, bool]:
        response = await self._request(
            RequestMethod.POST, 'editMessageText', params={
                'chat_id': chat_id, 'message_id': message_id,
                'inline_message_id': inline_message_id, 'text': text,
                'parse_mode': _parse_mode_to_str(parse_mode),
                'disable_web_page_preview': disable_web_page_preview,
                'reply_markup': _to_json(reply_markup)})

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def edit_message_caption(
        self, chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Union[Message, bool]:
        response = await self._request(
            RequestMethod.POST, 'editMessageCaption', params={
                'chat_id': chat_id, 'message_id': message_id,
                'inline_message_id': inline_message_id,
                'caption': caption,
                'parse_mode': _parse_mode_to_str(parse_mode),
                'reply_markup': _to_json(reply_markup)})

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def edit_message_media(
        self, chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        media: InputMedia = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        attachments: Optional[Dict[str, InputFile]] = None
    ) -> Union[Message, bool]:
        params: ParamsType = {
            'chat_id': chat_id, 'message_id': message_id,
            'inline_message_id': inline_message_id,
            'media': _to_json(media),
            'reply_markup': _to_json(reply_markup)
        }
        if attachments is not None:
            params.update(attachments)
        response = await self._request(
            RequestMethod.POST, 'editMessageMedia', params=params)

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def edit_message_reply_markup(
        self, chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Union[Message, bool]:
        response = await self._request(
            RequestMethod.POST, 'editMessageReplyMarkup', params={
                'chat_id': chat_id, 'message_id': message_id,
                'inline_message_id': inline_message_id,
                'reply_markup': _to_json(reply_markup)})

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def stop_poll(
        self, chat_id: Union[int, str],
        message_id: int = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Poll:
        response = await self._request(
            RequestMethod.POST, 'stopPoll', params={
                'chat_id': chat_id, 'message_id': message_id,
                'reply_markup': _to_json(reply_markup)})

        return response.result

    async def delete_message(self, chat_id: Optional[Union[int, str]] = None,
                             message_id: Optional[int] = None) -> bool:
        response = await self._request(RequestMethod.POST, 'deleteMessage',
                                       params={'chat_id': chat_id,
                                               'message_id': message_id})

        return response.result

    async def send_sticker(
        self, chat_id: Union[int, str],
        sticker: Union[InputFile, str],
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[ReplyMarkup] = None
    ) -> Message:
        response = await self._request(
            RequestMethod.POST, 'sendSticker', params={
                'chat_id': chat_id, 'sticker': sticker,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def get_sticker_set(self, name: str) -> StickerSet:
        response = await self._request(RequestMethod.GET, 'getStickerSet',
                                       params={'name': name})

        return StickerSet.from_dict(response.result)

    async def upload_sticker_file(self, user_id: int,
                                  png_sticker: InputFile) -> File:
        response = await self._request(RequestMethod.POST, 'uploadStickerFile',
                                       params={'user_id': user_id,
                                               'png_sticker': png_sticker})

        return File.from_dict(response.result)

    async def create_new_sticker_set(
        self, user_id: int, name: str, title: str,
        png_sticker: Union[InputFile, str], emojis: str,
        contains_masks: Optional[bool] = None,
        mask_position: Optional[MaskPosition] = None
    ) -> bool:
        response = await self._request(
            RequestMethod.POST, 'createNewStickerSet', params={
                'user_id': user_id, 'name': name, 'title': title,
                'png_sticker': png_sticker, 'emojis': emojis,
                'contains_masks': contains_masks,
                'mask_position': _to_json(mask_position)})

        return response.result

    async def add_sticker_to_set(
        self, user_id: int, name: str, title: str,
        png_sticker: Union[InputFile, str], emojis: str,
        mask_position: Optional[MaskPosition] = None
    ) -> File:
        response = await self._request(
            RequestMethod.POST, 'addStickerToSet', params={
                'user_id': user_id, 'name': name, 'title': title,
                'png_sticker': png_sticker, 'emojis': emojis,
                'mask_position': _to_json(mask_position)})

        return File.from_dict(response.result)

    async def set_sticker_position_in_set(self, sticker: str,
                                          position: int) -> bool:
        response = await self._request(
            RequestMethod.POST, 'setStickerPositionInSet',
            params={'sticker': sticker, 'position': position})

        return response.result

    async def delete_sticker_from_set(self, sticker: str) -> bool:
        response = await self._request(RequestMethod.POST,
                                       'deleteStickerFromSet',
                                       params={'sticker': sticker})

        return response.result

    async def answer_inline_query(
        self, inline_query_id: str, results: Iterable[InlineQueryResult],
        cache_time: Optional[int] = None, is_personal: Optional[bool] = None,
        next_offset: Optional[str] = None,
        switch_pm_text: Optional[str] = None,
        switch_pm_parameter: Optional[str] = None
    ) -> bool:
        response = await self._request(
            RequestMethod.POST, 'answerInlineQuery', params={
                'inline_query_id': inline_query_id,
                'results': json_dumps(tuple(result.to_dict()
                                            for result in results)),
                'cache_time': cache_time, 'is_personal': is_personal,
                'next_offset': next_offset, 'switch_pm_text': switch_pm_text,
                'switch_pm_parameter': switch_pm_parameter})

        return response.result

    async def send_invoice(
        self, chat_id: int, title: str, description: str, payload: str,
        provider_token: str, start_parameter: str, currency: str,
        prices: Iterable[LabeledPrice], provider_data: Optional[str] = None,
        photo_url: Optional[str] = None, photo_size: Optional[int] = None,
        photo_width: Optional[int] = None, photo_height: Optional[int] = None,
        need_name: Optional[bool] = None,
        need_phone_number: Optional[bool] = None,
        need_email: Optional[bool] = None,
        need_shipping_address: Optional[bool] = None,
        send_phone_number_to_provider: Optional[bool] = None,
        send_email_to_provider: Optional[bool] = None,
        is_flexible: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendInvoice', chat_id, params={
                'title': title, 'description': description, 'payload': payload,
                'provider_token': provider_token,
                'start_parameter': start_parameter,
                'currency': currency,
                'prices': json_dumps(tuple(price.to_dict()
                                           for price in prices)),
                'provider_data': provider_data,
                'photo_url': photo_url, 'photo_size': photo_size,
                'photo_width': photo_width, 'photo_height': photo_height,
                'need_name': need_name, 'need_phone_number': need_phone_number,
                'need_email': need_email,
                'need_shipping_address': need_shipping_address,
                'send_phone_number_to_provider': send_phone_number_to_provider,
                'send_email_to_provider': send_email_to_provider,
                'is_flexible': is_flexible,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def answer_shipping_query(
        self, inline_query_id: str, ok: bool,
        shipping_options: Optional[Iterable[ShippingOption]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        if shipping_options is not None:
            shipping_options_json: Optional[str] = json_dumps(tuple(
                item.to_dict() for item in shipping_options))
        else:
            shipping_options_json = None
        response = await self._request(
            RequestMethod.POST, 'answerShippingQuery', params={
                'inline_query_id': inline_query_id, 'ok': ok,
                'shipping_options': shipping_options_json,
                'error_message': error_message})

        return response.result

    async def answer_pre_checkout_query(
        self, pre_checkout_query_id: str, ok: bool,
        error_message: Optional[str] = None
    ) -> bool:
        response = await self._request(
            RequestMethod.POST, 'answerPreCheckoutQuery', params={
                'pre_checkout_query_id': pre_checkout_query_id, 'ok': ok,
                'error_message': error_message})

        return response.result

    async def set_passport_data_errors(
        self, user_id: int,
        errors: Iterable[PassportElementError]
    ) -> bool:
        response = await self._request(
            RequestMethod.POST, 'setPassportDataErrors', params={
                'user_id': user_id,
                'errors': json_dumps(tuple(error.to_dict()
                                           for error in errors))})

        return response.result

    async def send_game(
        self, chat_id: int, game_short_name: str,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Message:
        response = await self._safe_request(
            RequestMethod.POST, 'sendGame', chat_id, params={
                'game_short_name': game_short_name,
                'disable_notification': disable_notification,
                'reply_to_message_id': reply_to_message_id,
                'reply_markup': _to_json(reply_markup)})

        return Message.from_dict(response.result)

    async def set_game_score(
        self, user_id: int, score: int,
        force: Optional[bool] = None,
        disable_edit_message: Optional[bool] = None,
        chat_id: Optional[int] = None, message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None
    ) -> Union[Message, bool]:
        response = await self._request(
            RequestMethod.POST, 'setGameScore', params={
                'user_id': user_id, 'score': score,
                'force': force, 'disable_edit_message': disable_edit_message,
                'chat_id': chat_id, 'message_id': message_id,
                'inline_message_id': inline_message_id})

        if isinstance(response.result, bool):
            return response.result
        else:
            return Message.from_dict(response.result)

    async def get_game_high_scores(
        self, user_id: int, chat_id: Optional[int] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None
    ) -> Tuple[GameHighScore, ...]:
        response = await self._request(
            RequestMethod.POST, 'getGameHighScores', params={
                'user_id': user_id, 'chat_id': chat_id,
                'message_id': message_id,
                'inline_message_id': inline_message_id})

        return tuple(GameHighScore.from_dict(item) for item in response.result)
