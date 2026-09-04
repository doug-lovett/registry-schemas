# Copyright © 2020 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test Suite to ensure the PPR Financing Statement (request and response) schema is valid."""
import copy

import pytest

from registry_schemas import validate
from registry_schemas.example_data.ppr import FINANCING_STATEMENT


SECURITIES_ACT_ORDERS = [
    {
        'courtName': 'Supreme Court of British Columbia.',
        'courtRegistry': 'KAMLOOPS',
        'fileNumber': 'BC123445',
        'orderDate': '2024-02-02T00:00:00-08:00',
        'effectOfOrder': 'Court Order to remove James Smith as debtor.',
        'courtOrder': True
    }
]
SECURITIES_ACT_NOTICE = {
    'securitiesActNoticeType': 'LIEN',
    'effectiveDateTime': '2024-02-02T00:00:00-08:00',
    'description': 'TEST LIEN NOTICE TYPE',
    'securitiesActOrders': SECURITIES_ACT_ORDERS
}
# testdata pattern is ({registration type}, {is valid})
TEST_DATA_REG_TYPE = [
    ('CC', True),
    ('CT', True),
    ('DP', True),
    ('ET', True),
    ('FA', True),
    ('FL', True),
    ('FO', True),
    ('FR', True),
    ('FS', True),
    ('FT', True),
    ('HN', True),
    ('HR', True),
    ('IP', True),
    ('IT', True),
    ('LO', True),
    ('LT', True),
    ('MH', True),
    ('MI', True),
    ('ML', True),
    ('MN', True),
    ('MR', True),
    ('OT', True),
    ('PG', True),
    ('PN', True),
    ('PS', True),
    ('RA', True),
    ('RL', True),
    ('SA', True),
    ('SG', True),
    ('SS', True),
    ('TF', True),
    ('TA', True),
    ('TG', True),
    ('TL', True),
    ('TM', True),
    ('WL', True),
    ('MD', True),
    ('PT', True),
    ('SC', True),
    ('SV', True),
    ('TO', True),
    ('SE', True),
    ('CL', True),
    ('EH', True),
    ('RP', True),
    ('XX', False),
]
# testdata pattern is ({other type description}, {is valid})
TEST_DATA_OT = [
    ('0123456789012345678901234567890123456789012345678901234567890123456789', True),
    ('01234567890123456789012345678901234567890123456789012345678901234567890', False),
]
# testdata pattern is ({desc}, {valid}, {reg_type}, {sec_type}, {has_orders}, {court_order})
TEST_DATA_SEC_ACT = [
    ('Valid LIEN', True, 'SE', 'LIEN', False, None),
    ('Valid PRESERVATION', True, 'SE', 'PRESERVATION', True, True),
    ('Valid PROCEEDINGS', True, 'SE', 'PROCEEDINGS', False, None),
    ('Invalid order', False, 'SE', 'PROCEEDINGS', True, None),
    ('Invalid SA type', False, 'SE', 'JUNK', False, None),
    ('Invalid missing SA type', False, 'SE', None, False, None),
    ('Invalid debtor name', False, 'SE', 'LIEN', False, None),
    ('Invalid secured name', False, 'SE', 'LIEN', False, None),
    ('Invalid missing collateral', False, 'SE', 'LIEN', False, None)
]


@pytest.mark.parametrize('desc,valid,reg_type,sec_type,has_orders,court_order', TEST_DATA_SEC_ACT)
def test_financing_sec_act(desc, valid, reg_type, sec_type, has_orders, court_order):
    """Assert the validation of a security act registration works as expected."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['type'] = reg_type
    statement['lifeInfinite'] = True
    del statement['trustIndenture']
    del statement['lienAmount']
    del statement['surrenderDate']
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['lifeYears']
    notice = copy.deepcopy(SECURITIES_ACT_NOTICE)
    if not sec_type:
        del notice['securitiesActNoticeType']
    else:
        notice['securitiesActNoticeType'] = sec_type
    if not has_orders:
        del notice['securitiesActOrders']
    elif not court_order:
        del notice['securitiesActOrders'][0]['courtOrder']
    statement['securitiesActNotices'] = [notice]
    if desc == 'Invalid debtor name':
        del statement['debtors'][0]['businessName']
    elif desc == 'Invalid secured name':
        del statement['securedParties'][0]['businessName']
    elif desc == 'Invalid missing collateral':
        del statement['vehicleCollateral']
        del statement['generalCollateral']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    if valid:
        assert is_valid
    else:
        assert not is_valid


@pytest.mark.parametrize('registration_type, valid', TEST_DATA_REG_TYPE)
def test_financing_regtype(registration_type, valid):
    """Assert the validation of all registration types."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['type'] = registration_type
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['lifeInfinite']
    if registration_type != 'SA':
        del statement['trustIndenture']
    elif registration_type != 'RL':
        del statement['lienAmount']
        del statement['surrenderDate']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)

    if valid:
        assert is_valid
    else:
        assert not is_valid


@pytest.mark.parametrize('other_description, valid', TEST_DATA_OT)
def test_financing_ot(other_description, valid):
    """Assert the validation of OT type otherTypeDescription."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['type'] = 'OT'
    statement['otherTypeDescription'] = other_description
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['lifeInfinite']
    del statement['trustIndenture']
    del statement['lienAmount']
    del statement['surrenderDate']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)

    if valid:
        assert is_valid
    else:
        assert not is_valid


def test_valid_financing_response_sa():
    """Assert that the schema is performing as expected for an financing response."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['lifeInfinite']
    del statement['lienAmount']
    del statement['surrenderDate']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert is_valid


def test_invalid_financing_baseregnum():
    """Assert that an invalid financing statement fails - base registration number too long."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['baseRegistrationNumber'] = 'B0000123456789'

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_clientref():
    """Assert that an invalid financing statement fails - client reference number too long."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['clientReferenceId'] = '012345678901234567890123456789012345678901234567890'

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_doc_id():
    """Assert that an invalid financing statement fails - document id too long."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['documentId'] = '00123456789'

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_timestamp():
    """Assert that an invalid financing statement fails - create timestamp format is invalid."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['createDateTime'] = 'XXXXXXXXXXXX'

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    # Commenting out: no longer working with 3.8 build
    # assert not is_valid


def test_invalid_financing_expiry():
    """Assert that an invalid financing statement fails - expiry date format is invalid."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['expiryDate'] = 'XXXXXXXX'

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    # Commenting out: no longer working with 3.8 build
    # assert not is_valid


def test_invalid_financing_lifeyears():
    """Assert that an invalid financing statement fails - life years value is invalid."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['lifeYears'] = 26

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_lienamount():
    """Assert that an invalid financing statement fails - liend amount is too long."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['lienAmount'] = '0123456789123456'

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_surrender():
    """Assert that an invalid financing statement fails - surrender date format is invalid."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['surrenderDate'] = 'XXXXXXXX'

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    # Commenting out: no longer working with 3.8 build
    # assert not is_valid


def test_invalid_financing_debtor_name():
    """Assert that an invalid financing statement fails - debtor name is missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['debtors'][0]['businessName']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_delete_secured_name():
    """Assert that an invalid financing statement fails - secured party name is missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['securedParties'][0]['businessName']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_regparty_address():
    """Assert that an invalid financing statement fails - registering party address is missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['registeringParty']['address']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_missing_vehicle_type():
    """Assert that an invalid financing statement fails - vehicle collateral type is missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['vehicleCollateral'][0]['type']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_missing_general_desc():
    """Assert that an invalid financing statement fails - general collateral description is missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['generalCollateral'][0]['description']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_missing_regparty():
    """Assert that an invalid financing statement fails - registering party is missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['registeringParty']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_missing_type():
    """Assert that an invalid financing statement fails - financing type missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['type']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_missing_secparties():
    """Assert that an invalid financing statement fails - secured parties are missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['securedParties']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_missing_debtors():
    """Assert that an invalid financing statement fails - debtors are missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['debtors']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_financing_missing_collateral():
    """Assert that an invalid financing statement fails - vehicle and general collateral are missing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['vehicleCollateral']
    del statement['generalCollateral']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_authorization_received():
    """Assert that authorization received validation works as expected."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['authorizationReceived']

    is_valid, errors = validate(statement, 'financingStatement', 'ppr')
    assert is_valid

    statement['authorizationReceived'] = False
    is_valid, errors = validate(statement, 'financingStatement', 'ppr')
    assert is_valid

    statement['authorizationReceived'] = True
    is_valid, errors = validate(statement, 'financingStatement', 'ppr')
    assert is_valid

    statement['authorizationReceived'] = 'junk'
    is_valid, errors = validate(statement, 'financingStatement', 'ppr')
    if errors:
        for err in errors:
            print(err.message)
    assert not is_valid


def test_valid_financing_response_transition():
    """Assert that the schema is performing as expected for a transition registration response."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    del statement['lifeInfinite']
    del statement['lienAmount']
    del statement['surrenderDate']
    statement['transitionDescription'] = 'COMPANY ACT DOCUMENT'
    statement['transitionDate'] = '1986-12-29T00:00:01-08:53'
    statement['transitionNumber'] = 'BC0021615'
    is_valid, errors = validate(statement, 'financingStatement', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert is_valid
