from enum import IntEnum
from packages.util.utils.create_flow_status import create_flow_status

class TestCase1Enum(IntEnum):
    INIT = 0
    VERIFY = 1
    END = 2


class TestCase2Enum(IntEnum):
    INIT = 0
    VERIFY = 1
    VERIFY_ADDRESS = 2
    CARD_TAP = 3
    END = 4


class SEED_GENERATION(IntEnum):
    INIT = 0
    PASSPHRASE = 1
    CARD = 2


class TestCase3Enum(IntEnum):
    INIT = 0
    VERIFY = 1
    VERIFY_ADDRESS = 2
    TEST_3_SEED_GENERATED = 3
    END = 4


class TestCase3EnumWithSeed(IntEnum):
    INIT = 0
    VERIFY = 1
    VERIFY_ADDRESS = 2
    PASSPHRASE = 3
    CARD = 4
    END = 5


fixtures = {
    "valid": [
        {
            "name": "with onStatus update",
            "enum": TestCase1Enum,
            "operationEnum": TestCase1Enum,
            "statusCalls": [{"flowStatus": TestCase1Enum.VERIFY}],
            "forceStatusUpdateCalls": [],
            "eventCalls": [[TestCase1Enum.INIT], [TestCase1Enum.VERIFY]],
        },
        {
            "name": "with forceStatusUpdate",
            "enum": TestCase2Enum,
            "operationEnum": TestCase2Enum,
            "statusCalls": [],
            "forceStatusUpdateCalls": [TestCase2Enum.CARD_TAP],
            "eventCalls": [
                [TestCase2Enum.INIT],
                [TestCase2Enum.VERIFY],
                [TestCase2Enum.VERIFY_ADDRESS],
                [TestCase2Enum.CARD_TAP],
            ],
        },
        {
            "name": "with seed generation enum",
            "enum": TestCase3EnumWithSeed,
            "operationEnum": TestCase3Enum,
            "seedGenerationEnum": SEED_GENERATION,
            "statusCalls": [
                {
                    "flowStatus": create_flow_status(
                        TestCase3Enum.VERIFY,
                        SEED_GENERATION.INIT,
                    ),
                },
                {
                    "flowStatus": create_flow_status(
                        TestCase3Enum.VERIFY_ADDRESS,
                        SEED_GENERATION.INIT,
                    ),
                },
                {
                    "flowStatus": create_flow_status(
                        TestCase3Enum.TEST_3_SEED_GENERATED,
                        SEED_GENERATION.CARD,
                    ),
                },
                {
                    "flowStatus": create_flow_status(
                        TestCase3Enum.END,
                        SEED_GENERATION.INIT
                    ),
                },
            ],
            "forceStatusUpdateCalls": [],
            "eventCalls": [
                [TestCase3EnumWithSeed.INIT],
                [TestCase3EnumWithSeed.VERIFY],
                [TestCase3EnumWithSeed.VERIFY_ADDRESS],
                [TestCase3EnumWithSeed.PASSPHRASE],
                [TestCase3EnumWithSeed.CARD],
                [TestCase3EnumWithSeed.END],
            ],
        },
    ],
}
