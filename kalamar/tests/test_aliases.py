# -*- coding: utf-8 -*-
# This file is part of Dyko
# Copyright © 2008-2009 Kozea
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kalamar.  If not, see <http://www.gnu.org/licenses/>.

from nose.tools import eq_, nottest
from kalamar import Site, Item
from kalamar.property import Property
from kalamar.request import Condition, And, Or, Not, Request
from kalamar.access_point.memory import Memory
from kalamar.access_point.aliases import AliasedItem, Aliases
from .test_memory import make_test_site

class DummyAP(object):
    pass

def test_aliased_item():
    dummy_underlying_ap = DummyAP()
    dummy_underlying_ap.properties = {'FOO': Property(int), 'other': Property(int)}
    dummy_ap = DummyAP()
    dummy_ap.properties = {'foo': None, 'other': None}
    dummy_ap.aliases = {'foo': 'FOO'}
    dummy_ap.reversed_aliases = {'FOO': 'foo'}
    underlying_item = Item(dummy_underlying_ap, {'FOO': 9, 'other': 0})
    item = AliasedItem(dummy_ap, underlying_item)
    # aliased property
    eq_(underlying_item['FOO'], 9)
    item['foo'] = 1
    eq_(underlying_item['FOO'], 1)
    # old names are masked
    try:
        item['FOO']
    except KeyError:
        pass
    else:
        assert False, 'expected KeyError'
    # non aliased property
    eq_(underlying_item['other'], 0)
    item['other'] = 2
    eq_(underlying_item['other'], 2)
    # other attr
    assert item.access_point is dummy_ap
    # MultiDict-like method, aliased property
    item.setlist('foo', (2, 3))
    eq_(item['foo'], 2)
    eq_(item.getlist('foo'), (2, 3))
    eq_(underlying_item['FOO'], 2)
    eq_(underlying_item.getlist('FOO'), (2, 3))


def test_translate_request():
    ap = Aliases({'foo': 'FOO', 'bar': 'BAR'}, Memory({}, ''))
    C = Condition
    eq_(ap.translate_request(C('foo', '=', 4)), C('FOO', '=', 4))
    eq_(ap.translate_request(C('other', '=', 7)), C('other', '=', 7))
    eq_(
        ap.translate_request(And(
            C('foo', '=', 4),
            Not(Or(C('other', '=', 7), C('bar', '!=', 1)))
        )),
        And(
            Condition('FOO', '=', 4), 
            Not(Or(C('other', '=', 7), C('BAR', '!=', 1)))
        )
    )


def test_aliased_memory():
    site = make_test_site()
    underlying_ap = site.access_points['things']
    ap = Aliases({'nom': 'name'}, underlying_ap)
    site.register('aliased', ap)
    
    results = site.search('aliased', {'nom': 'bar'})
    eq_(set(item['id'] for item in results), set([2, 3]))

    # old names are masked
    try:
        site.search('aliased', {'name': 'bar'})
    except KeyError:
        pass
    else:
        assert False, 'KeyError expected.'

