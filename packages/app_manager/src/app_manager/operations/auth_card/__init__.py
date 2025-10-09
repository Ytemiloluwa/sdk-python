from typing import Optional, Dict, Tuple
from core.types import ISDK
from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType

from util.utils import (
    assert_condition,
    create_logger_with_prefix,
    create_status_listener,
    ForceStatusUpdate,
    OnStatus,
)

from app_manager.constants.appId import APP_VERSION
from app_manager.proto.generated.types import AuthCardStatus
from ...services import card_auth as card_auth_service
from ...utils import (
    assert_or_throw_invalid_result,
    logger as root_logger,
    OperationHelper,
)
from .types import IAuthCardParams, AuthCardEventHandler

# Re-export types
__all__ = ['IAuthCardParams', 'AuthCardEventHandler', 'auth_card']

logger = create_logger_with_prefix(root_logger, 'AuthCard')


class CardNotVerifiedError(Exception):
    def __init__(self, message: str = 'Card not verified'):
        super().__init__(message)
        self.message = message


async def verify_serial_signature(
    helper: OperationHelper,
    on_status: OnStatus,
    force_status_update: ForceStatusUpdate,
    card_number: Optional[int] = None,
    is_pair_required: Optional[bool] = None,
) -> Tuple[bytes, bytes]:
    """
    Verify serial signature from card.
    
    Args:
        helper: Operation helper for SDK communication
        on_status: Status callback function
        force_status_update: Function to force status updates
        card_number: Optional card number (1-4)
        is_pair_required: Whether card pairing is required
        
    Returns:
        Tuple of (serial, challenge) bytes
        
    Raises:
        CardNotVerifiedError: If card verification fails
    """
    # Send initiate query
    query = {
        'initiate': {
            'card_index': card_number,
            'is_pair_required': is_pair_required
        }
    }
    await helper.send_query(query)

    # Wait for response
    result = await helper.wait_for_result(on_status = OnStatus)
    logger.verbose('AuthCardResponse', {'result': result})
    assert_or_throw_invalid_result(result.serial_signature)

    # Update status
    force_status_update(AuthCardStatus.AUTH_CARD_STATUS_SERIAL_SIGNED)

    # Verify serial signature with service
    verification_params = {
        'serial': result.serial_signature.serial,
        'signature': result.serial_signature.signature,
    }
    challenge = await card_auth_service.verify_card_serial_signature(**verification_params)
    serial = result.serial_signature.serial

    if not challenge:
        raise CardNotVerifiedError()

    return serial, challenge


async def verify_challenge_signature(
    helper: OperationHelper,
    on_status: OnStatus,
    force_status_update: ForceStatusUpdate,
    challenge: bytes,
    serial: bytes,
    email: Optional[str] = None,
    cysync_version: Optional[str] = None,
    only_failure: Optional[bool] = None,
    session_id: Optional[str] = None,
) -> str:
    """
    Verify challenge signature from card.
    
    Args:
        helper: Operation helper for SDK communication
        on_status: Status callback function
        force_status_update: Function to force status updates
        challenge: Challenge bytes from previous step
        serial: Serial bytes from previous step
        email: Optional user email
        cysync_version: Optional CySync version
        only_failure: Optional flag for failure-only mode
        session_id: Optional existing session ID
        
    Returns:
        New session ID string
        
    Raises:
        CardNotVerifiedError: If challenge verification fails
    """
    # Send challenge query
    query = {'challenge': {'challenge': challenge}}
    await helper.send_query(query)

    # Wait for response
    result = await helper.wait_for_result(on_status=OnStatus)
    logger.verbose('AuthCardResponse', {'result': result})
    assert_or_throw_invalid_result(result.challenge_signature)
    force_status_update(AuthCardStatus.AUTH_CARD_STATUS_CHALLENGE_SIGNED)

    # Verify challenge signature with service
    verification_params = {
        'signature': result.challenge_signature.signature,
        'challenge': challenge,
        'serial': serial,
        'cysync_version': cysync_version,
        'only_failure': only_failure,
        'session_id': session_id,
        'email': email,
    }
    verification_result = await card_auth_service.verify_card_challenge_signature(**verification_params)
    
    is_verified = verification_result.get('is_verified', False)
    new_session_id = verification_result.get('session_id', '')

    if not is_verified:
        raise CardNotVerifiedError()

    return new_session_id


async def auth_card(sdk: ISDK, params: Optional[IAuthCardParams] = None) -> Dict[str, str]:
    """

    This function performs a two-step card authentication process:
    1. Verify serial signature from the card
    2. Verify challenge signature 
    
    Args:
        sdk: The SDK instance for device communication
        params: Optional authentication parameters
        
    Returns:
        Dictionary containing the new session_id
        
    Raises:
        DeviceAppError: When card authentication fails
        Exception: For other errors during authentication
    """
    if params and params.card_number is not None:
        assert_condition(
            1 <= params.card_number <= 4,
            'Card number should be one of 1,2,3,4'
        )

    # Check app compatibility
    await sdk.check_app_compatibility(APP_VERSION)

    # Create operation helper
    helper = OperationHelper(sdk, 'auth_card', 'auth_card')

    try:
        log_params = {}
        if params:
            log_params = {
                'card_number': params.card_number,
                'is_pair_required': params.is_pair_required,
                'email': params.email,
                'cysync_version': params.cysync_version,
                'only_failure': params.only_failure,
                'session_id': params.session_id,
            }
        logger.info('Started', log_params)

        # Create status listener with proper parameters
        status_listener_config = {
            'enums': AuthCardStatus,
            'onEvent': params.on_event if params else None,
            'logger': logger,
        }
        status_listener_result = create_status_listener(status_listener_config)
        on_status = status_listener_result['onStatus']
        force_status_update = status_listener_result['forceStatusUpdate']

        # Step 1: Verify serial signature
        serial, challenge = await verify_serial_signature(
            helper=helper,
            on_status=on_status,
            force_status_update=force_status_update,
            card_number=params.card_number if params else None,
            is_pair_required=params.is_pair_required if params else None,
        )

        # Step 2: Verify challenge signature  
        new_session_id = await verify_challenge_signature(
            helper=helper,
            on_status=on_status,
            force_status_update=force_status_update,
            serial=serial,
            challenge=challenge,
            email=params.email if params else None,
            cysync_version=params.cysync_version if params else None,
            only_failure=params.only_failure if params else None,
            session_id=params.session_id if params else None,
        )

        # Send final verification result
        await helper.send_query({'result': {'verified': True}})
        result = await helper.wait_for_result()
        assert_or_throw_invalid_result(result.flow_complete)
        force_status_update(AuthCardStatus.AUTH_CARD_STATUS_PAIRING_DONE)

        logger.info('Completed', {'verified': True})
        return {'session_id': new_session_id}

    except CardNotVerifiedError:
        await helper.send_query({'result': {'verified': False}})
        result = await helper.wait_for_result()
        logger.verbose('AuthCardResponse', {'result': result})
        assert_or_throw_invalid_result(result.flow_complete)

        logger.info('Completed', {'verified': False})
        raise DeviceAppError(DeviceAppErrorType.CARD_AUTH_FAILED)

    except Exception as error:
        logger.info('Failed')

        try:
            await sdk.send_abort()
        except Exception:
            pass

        raise error
