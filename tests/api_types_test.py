from typing import Any, Dict, List, Optional, Tuple, Union

import attr
import pytest

from aiotgbot.api_types import (BaseTelegram, CallbackQuery,
                                ChosenInlineResult, DataMappingError,
                                InlineQuery, Message, PreCheckoutQuery,
                                ShippingQuery, _is_attr_union, _is_optional,
                                _is_tuple, _is_union)


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Class1(BaseTelegram):
    a: int
    b: Optional[int]
    c: Optional[str]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Class2(BaseTelegram):
    a: int
    y: float
    z: Optional[bool]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Class3(BaseTelegram):
    a: int
    b: Optional[int]
    c: Optional[str]
    d: Tuple[Class1, ...]
    e: Optional[Tuple[Class1, ...]]
    f: Optional[Class1]
    g: Union[Class1, Class2]
    h: Optional[Union[Class1, Class2]]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Class4(BaseTelegram):
    a: int
    b: Optional[int]
    c_: Optional[str]


@attr.s(slots=True, frozen=True, auto_attribs=True)
class Class5(BaseTelegram):
    a: int
    b: Optional[str]
    c: Class1
    d: Tuple[Class1, ...]
    e: List[List[int]]
    f: Optional[Dict]


@pytest.mark.parametrize('test, expected', (
    (Tuple[int], True),
    (Union[int, str], False),
    (int, False),
    (type(None), False)
))
def test_is_tuple(test, expected):
    assert _is_tuple(test) is expected


@pytest.mark.parametrize('test, expected', (
    (Union[int, str], True),
    (List[str], False),
    (int, False),
    (type(None), False)
))
def test_is_union(test, expected):
    assert _is_union(test) is expected


@pytest.mark.parametrize('test, expected', (
    (Union[int, str, None], True),
    (Optional[int], True),
    (Union[int, str], False),
    (List[str], False),
    (int, False),
    (type(None), False),
))
def test_is_optional(test, expected):
    assert _is_optional(test) is expected


@pytest.mark.parametrize('test, expected', (
    (Union[Class1, Class2], True),
    (Union[Class1, Class2, None], True),
    (Optional[int], False),
    (Union[int, str], False),
    (int, False),
    (type(None), False)
))
def test_is_attr_union(test, expected):
    assert _is_attr_union(test) is expected


def test_base_to_dict():
    tc1 = Class5(
        a=1,
        b='str',
        c=Class1(a=1, b=2, c='3'),
        d=(Class1(a=1, b=2, c='3'), Class1(a=2, b=3, c='4')),
        e=[[1, 2], [3, 4]],
        f=None
    )
    assert tc1.to_dict() == {
        'a': 1,
        'b': 'str',
        'c': {'a': 1, 'b': 2, 'c': '3'},
        'd': [{'a': 1, 'b': 2, 'c': '3'}, {'a': 2, 'b': 3, 'c': '4'}],
        'e': [[1, 2], [3, 4]]
    }


def test_base_to_dict_exception():
    with pytest.raises(TypeError, match='"{3: 4}" has unsupported type'):
        Class5(
            a=1,
            b=None,
            c=Class1(a=1, b=2, c='3'),
            d=(Class1(a=1, b=2, c='3'), Class1(a=2, b=3, c='4')),
            e=[[1, 2], [3, 4]],
            f={3: 4}
        ).to_dict()
    with pytest.raises(TypeError, match='"{5: 6}" has unsupported type'):
        Class5(
            a=1,
            b=None,
            c=Class1(a=1, b=2, c='3'),
            d=(Class1(a=1, b=2, c='3'), Class1(a=2, b=3, c='4')),
            e=[[1, 2], {5: 6}],
            f=None
        ).to_dict()


def test_get_type_hints():
    assert list(Class4.get_type_hints()) == [
        ('a', 'a', int),
        ('b', 'b', Union[int, type(None)]),
        ('c', 'c_', Union[str, type(None)])
    ]


def test_base_from_dict():
    assert (Class1.from_dict({'a': 1, 'b': 2}) ==
            Class1(a=1, b=2, c=None))
    with pytest.raises(DataMappingError):
        Class1.from_dict({'b': 2, 'c': '3'})


def test_base_handle_object():
    assert (BaseTelegram.handle_object(Class1, {'a': 1, 'c': 'c'}) ==
            Class1(a=1, b=None, c='c'))
    with pytest.raises(DataMappingError,
                       match='Data without required keys: a'):
        BaseTelegram.handle_object(Class1, {'b': 2})


def test_base_handle_field():
    assert BaseTelegram.handle_field(int, 1) == 1
    message = '"some str" is not instance of type "int"'
    with pytest.raises(DataMappingError, match=message):
        BaseTelegram.handle_field(int, 'some str')

    assert BaseTelegram.handle_field(type(None), None) is None
    with pytest.raises(DataMappingError, match='111" is not None'):
        BaseTelegram.handle_field(type(None), 111)

    assert BaseTelegram.handle_field(Tuple[str], ['str']) == ('str',)
    assert BaseTelegram.handle_field(List[str], ['str']) == ['str']
    with pytest.raises(DataMappingError, match='Data "some str" is not list'):
        BaseTelegram.handle_field(Tuple[str], 'some str')

    assert BaseTelegram.handle_field(Any, {1: 2}) == {1: 2}
    assert BaseTelegram.handle_field(Optional[str], None) is None

    assert (BaseTelegram.handle_field(Class1, {'a': 1}) ==
            Class1(a=1, b=None, c=None))

    union: Union[Any] = Union[Class1, Class2, None]
    assert (BaseTelegram.handle_field(union, {'a': 1}) ==
            Class1(a=1, b=None, c=None))
    assert (BaseTelegram.handle_field(union, {'a': 1, 'y': .1}) ==
            Class2(a=1, y=.1, z=None))
    message = ('Data "{\'a\': 1, \'ooo\': 0.1}\" not match any of '
               '"Class1, Class2, NoneType"')
    with pytest.raises(DataMappingError, match=message):
        BaseTelegram.handle_field(union, {'a': 1, 'ooo': .1})

    message = r'Data "None" not match field type "typing\.Union\[str, int\]"'
    with pytest.raises(DataMappingError, match=message):
        BaseTelegram.handle_field(Union[str, int], None)


def test_base():
    t3_dict = {
        'a': 1,
        'b': 2,
        'c': 'some str',
        'd': [{'a': 1, 'b': 2, 'c': '3'}, {'a': 2, 'b': 3, 'c': '4'}],
        'e': [{'a': 3, 'b': 4, 'c': '5'}, {'a': 4, 'b': 5, 'c': '6'}],
        'f': {'a': 5, 'b': 6},
        'g': {'a': 6, 'y': .7, 'z': False},
        'h': {'a': 7, 'b': 8, 'c': '9'}
    }
    t3 = Class3(
        a=1,
        b=2,
        c='some str',
        d=(Class1(a=1, b=2, c='3'), Class1(a=2, b=3, c='4')),
        e=(Class1(a=3, b=4, c='5'), Class1(a=4, b=5, c='6')),
        f=Class1(a=5, b=6, c=None),
        g=Class2(a=6, y=.7, z=False),
        h=Class1(a=7, b=8, c='9')
    )
    assert Class3.from_dict(t3_dict) == t3


@pytest.mark.parametrize('_str, _type, in_keys, in_fields', (
    ('from', Message, True, False),
    ('from_', Message, False, True),
    ('from', CallbackQuery, True, False),
    ('from_', CallbackQuery, False, True),
    ('from', InlineQuery, True, False),
    ('from_', InlineQuery, False, True),
    ('from', ChosenInlineResult, True, False),
    ('from_', ChosenInlineResult, False, True),
    ('from', ShippingQuery, True, False),
    ('from_', ShippingQuery, False, True),
    ('from', PreCheckoutQuery, True, False),
    ('from_', PreCheckoutQuery, False, True)
))
def test_fixed_hints(_str, _type, in_keys, in_fields):
    assert (_str in [k for k, f, t in _type.get_type_hints()]) is in_keys
    assert (_str in [f for k, f, t in _type.get_type_hints()]) is in_fields
