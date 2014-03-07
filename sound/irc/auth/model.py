# encoding: utf-8

from __future__ import unicode_literals

import re
from datetime import datetime
from random import choice
from string import printable
from mongoengine import BinaryField
from mongoengine.base import BaseField
from scrypt import error as scrypt_error, encrypt as scrypt, decrypt as validate_scrypt

from web.core import config
from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, IntField, EmbeddedDocumentField, ListField
from brave.api.client import API


log = __import__('logging').getLogger(__name__)


# TODO: Deduplication?  Only store integer ID, turn Entity into its own collection.
# Would require migration map/reduce and scrubbing query.

class Entity(EmbeddedDocument):
    meta = dict(allow_inheritance=False)
    
    id = IntField(db_field='i')
    name = StringField(db_field='n')


class Ticket(Document):
    meta = dict(
            collection = 'Tickets',
            allow_inheritance = False,
            indexes = [
                    'character.id'
                ],
        )
    
    token = StringField(db_field='t')
    
    character = EmbeddedDocumentField(Entity, db_field='c', default=lambda: Entity())
    corporation = EmbeddedDocumentField(Entity, db_field='o', default=lambda: Entity())
    alliance = EmbeddedDocumentField(Entity, db_field='a', default=lambda: Entity())
    tags = ListField(StringField(), db_field='g', default=list)
    
    comment = StringField(db_field='m', default='')
    
    expires = DateTimeField(db_field='e')
    seen = DateTimeField(db_field='s')  # TODO: Update this when the user connects/disconnects.
    registered = DateTimeField(db_field='r')

    def transform_to_nick(self):
      return re.sub('[^A-Za-z0-9]+', '_', self.character.name.lower())
    
    def __repr__(self):
        return "<Ticket {0.id} \"{0.character.name}\">".format(self)
    
    @classmethod
    def authenticate(cls, identifier, password=None):
        """Validate the given identifier; password is ignored."""
        
        api = API(config['api.endpoint'], config['api.identity'], config['api.private'], config['api.public'])
        result = api.core.info(identifier)
        
        user = cls.objects(character__id=result.character.id).first()
        
        if not user:
            user = cls(token=identifier, expires=result.expires, seen=datetime.utcnow())
        
        user.character.id = result.character.id
        user.character.name = result.character.name
        user.corporation.id = result.corporation.id
        user.corporation.name = result.corporation.name
        
        if result.alliance:
            user.alliance.id = result.alliance.id
            user.alliance.name = result.alliance.name
        
        user.tags = [i.replace('irc.', '') for i in (result.tags if 'tags' in result else [])]
        user.save()
        
        return user.id, user
    
    @classmethod
    def lookup(cls, identifier):
        """Thaw current user data based on session-stored user ID."""
        
        user = cls.objects(id=identifier).first()
        
        if user:
            user.update(set__seen=datetime.utcnow())
        
        return user
