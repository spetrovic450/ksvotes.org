import os
from app import db
from datetime import datetime
import json
from sqlalchemy.dialects.postgresql import JSON
from cryptography.fernet import Fernet
from sqlalchemy.ext.hybrid import hybrid_property,Comparator


def encryptem(data):
    f = Fernet(os.environ.get("CRYPT_KEY").encode())
    encrypted = f.encrypt(json.dumps(data).encode())
    return encrypted.decode()

def decryptem(data):
    f = Fernet(os.environ.get("CRYPT_KEY").encode())
    return f.decrypt(data.encode())

class Registrant(db.Model):
    __tablename__ = "registrants"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_completed_step = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime, default=None)

    #registration steps
    is_citizen = db.Column(db.Boolean, default=True)
    is_eighteen = db.Column(db.Boolean, default=True)
    party = db.Column(db.String()) #enum dem, rep, lib, unaf, green, other
    county = db.Column(db.String()) #may require some geo lookup.
    lang = db.Column(db.String()) #enum? (values?)
    signed_at = db.Column(db.DateTime, default=datetime.utcnow()) #converted to local time on image generated submission

    registration = db.Column(db.String())
    #create key from environmental key
    #json stringyify dictionary and encrypt

    @hybrid_property
    def registration_value(self):
        reg = decryptem(self.registration)
        return json.loads(reg.decode())

    @registration_value.setter
    def registration_value(self, data):
        self.registration = encryptem(data)

    class encrypt_comparator(Comparator):
        def operate(self, op, other, **kw):
            return op(
                self.__clause_element__(), encryptem(other),
                **kw
            )

    @registration_value.comparator
    def registration_value(cls):
        return cls.encrypt_comparator(
                    cls.registration
                )



    #defaults

    # registration JSON column encrypted and includes
    # {
    #     #section 1 federal form
    #     "prefix": "String",
    #     "suffix": "String",
    #     "name_first": "String",
    #     "name_middle": "String",
    #     "name_last": "String",
    #     "name_middle": "String",
    ##section 2 federal form
    #     "address_home": "String",
    #     "address_apt_lot": "String",
    #     "address_city_town": "String",
    #     "address_state": "String",
                #default KANSAS
    #     "address_zipcode": "String",
    ##section 3 federal form
    #     "mail_address": "String",
    #     "mail_address_city_town": "String",
    #     "mail_address_state": "String",
    #     "mail_address_zipcode": "String",
    ##section 4 federal form
    #     "dob": "String",
                #formatted MM-DD-YYYY
    ##section 5 federal form
    #     "telephone": "String",
                #formatted NNN-NNN-NNNN
    ##section 6 federal form
    #     "id_number": "String",
    ##section 7 federal form party: SKIPPED FOR NON PII
    ##section 8 federal form race: SKIPPED FOR NON PII
    ##section 9 federal form date signed: PARTIALLY SKIPPED FOR NON PII
    #     "signature_path": "String",
                #url to signature image (deleted on form submission)
    ##section A federal form
    #     "previous_prefix": "String",
    #     "previous_suffix": "String",
    #     "previous_name_first": "String",
    #     "previous_name_middle": "String",
    #     "previous_name_last": "String",
    #     "previous_name_middle": "String",
    ##section B federal form
    #     "previous_address_home": "String",
    #     "previous_address_apt_lot": "String",
    #     "previous_address_city_town": "String",
    #     "previous_address_state": "String",
                #default KANSAS
    #     "previous_address_zipcode": "String",
    ##section d federal form
    #     "helper": "String"
                #long string of help pii
    # }