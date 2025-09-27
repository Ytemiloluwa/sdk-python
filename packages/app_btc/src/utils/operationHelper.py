from typing import List, Dict, Any, TypeVar, Generic, Optional
from packages.core.src.sdk import ISDK
from packages.interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType
from packages.util.utils.create_status_listener import OnStatus
from packages.app_btc.src.proto.generated.btc import Query, Result
from packages.app_btc.src.proto.generated.common import ChunkPayload
from packages.app_btc.src.utils.assert_utils import assert_or_throw_invalid_result, parse_common_error

Q = TypeVar('Q')
R = TypeVar('R')


def decode_result(data: bytes) -> Result:
    """
    Decode result from device response.
    
    Args:
        data: Raw bytes from device
        
    Returns:
        Decoded result
        
    Raises:
        DeviceAppError: If decoding fails
    """
    try:
        return Result.parse(data)
    except TypeError:
        try:
            return Result().parse(data)
        except Exception:
            raise DeviceAppError(DeviceAppErrorType.INVALID_MSG_FROM_DEVICE)
    except Exception:
        raise DeviceAppError(DeviceAppErrorType.INVALID_MSG_FROM_DEVICE)


def encode_query(query: Dict[str, Any]) -> bytes:
    """
    Encode query to send to device.
    
    Args:
        query: Query dictionary
        
    Returns:
        Encoded query bytes
    """
    if 'get_public_key' in query:
        from packages.app_btc.src.proto.generated.btc import GetPublicKeyRequest, GetPublicKeyIntiateRequest
        get_pub_key_data = query['get_public_key']
        if 'initiate' in get_pub_key_data:
            initiate_data = get_pub_key_data['initiate']
            initiate = GetPublicKeyIntiateRequest(
                wallet_id=initiate_data['wallet_id'],
                derivation_path=initiate_data['derivation_path']
            )
            request = GetPublicKeyRequest(initiate=initiate)
            query_obj = Query(get_public_key=request)
        else:
            query_obj = Query()
    elif 'get_xpubs' in query:
        from packages.app_btc.src.proto.generated.btc import GetXpubsRequest, GetXpubsIntiateRequest, GetXpubDerivationPath
        get_xpubs_data = query['get_xpubs']
        if 'initiate' in get_xpubs_data:
            initiate_data = get_xpubs_data['initiate']
            derivation_paths = [GetXpubDerivationPath(path=dp['path']) for dp in initiate_data['derivation_paths']]
            initiate = GetXpubsIntiateRequest(
                wallet_id=initiate_data['wallet_id'],
                derivation_paths=derivation_paths
            )
            request = GetXpubsRequest(initiate=initiate)
            query_obj = Query(get_xpubs=request)
        else:
            query_obj = Query()
    elif 'sign_txn' in query:
        from packages.app_btc.src.proto.generated.btc import SignTxnRequest, SignTxnInitiateRequest
        sign_txn_data = query['sign_txn']
        if 'initiate' in sign_txn_data:
            initiate_data = sign_txn_data['initiate']
            initiate = SignTxnInitiateRequest(
                wallet_id=initiate_data['wallet_id'],
                derivation_path=initiate_data['derivation_path']
            )
            request = SignTxnRequest(initiate=initiate)
            query_obj = Query(sign_txn=request)
        else:
            query_obj = Query()
    else:
        query_obj = Query()
    
    return bytes(query_obj)


class OperationHelper(Generic[Q, R]):
    """
    Helper class for device operations with query/result pattern.
    """
    
    CHUNK_SIZE = 2048
    
    def __init__(self, sdk: ISDK, query_key: str, result_key: str, on_status: Optional[OnStatus] = None):
        """
        Initialize operation helper.
        
        Args:
            sdk: SDK instance
            query_key: Key for query type
            result_key: Key for result type
            on_status: Optional status callback
        """
        self.sdk = sdk
        self.query_key = query_key
        self.result_key = result_key
        self.on_status = on_status
    
    async def send_query(self, query: Dict[str, Any]) -> None:
        """
        Send query to device.
        
        Args:
            query: Query data
        """
        op_key = self.query_key
        if op_key == 'getPublicKey':
            op_key = 'get_public_key'
        elif op_key == 'getXpubs':
            op_key = 'get_xpubs'
        elif op_key == 'signTxn':
            op_key = 'sign_txn'
        query_data = {op_key: query}
        encoded_query = encode_query(query_data)
        await self.sdk.send_query(encoded_query)
    
    async def wait_for_result(self) -> Any:
        """
        Wait for and decode result from device.
        
        Returns:
            Decoded result data
            
        Raises:
            DeviceAppError: If result is invalid or contains errors
        """
        result_data = await self.sdk.wait_for_result({"on_status": self.on_status})
        result = decode_result(result_data)

        result_key = self.result_key
        if result_key == 'getPublicKey':
            result_key = 'get_public_key'
        elif result_key == 'getXpubs':
            result_key = 'get_xpubs'
        elif result_key == 'signTxn':
            result_key = 'sign_txn'

        if '.' in result_key:
            parts = result_key.split('.')
            result_value = result
            for part in parts:
                result_value = getattr(result_value, part, None)
                if result_value is None:
                    break
        else:
            result_value = getattr(result, result_key, None)
        
        # Check for errors in the specific operation response first
        if result_value and hasattr(result_value, 'common_error'):
            parse_common_error(result_value.common_error)
        
        # Check for errors in the top-level result
        parse_common_error(getattr(result, 'common_error', None))
        
        assert_or_throw_invalid_result(result_value)
        
        return result_value
    
    @staticmethod
    def split_into_chunks(data: bytes) -> List[bytes]:
        """
        Split data into chunks for transmission.
        
        Args:
            data: Data to split
            
        Returns:
            List of data chunks
        """
        chunks = []
        total_chunks = (len(data) + OperationHelper.CHUNK_SIZE - 1) // OperationHelper.CHUNK_SIZE
        
        for i in range(total_chunks):
            start = i * OperationHelper.CHUNK_SIZE
            end = min(start + OperationHelper.CHUNK_SIZE, len(data))
            chunk = data[start:end]
            chunks.append(chunk)
        
        return chunks
    
    async def send_in_chunks(self, data: bytes, query_key: str, result_key: str) -> None:
        """
        Send data in chunks to device.
        
        Args:
            data: Data to send
            query_key: Query key for chunk sending
            result_key: Result key for chunk acknowledgment
        """
        chunks = self.split_into_chunks(data)
        remaining_size = len(data)
        
        for i, chunk in enumerate(chunks):
            remaining_size -= len(chunk)
            
            chunk_payload = ChunkPayload(
                chunk=chunk,
                chunk_index=i,
                total_chunks=len(chunks),
                remaining_size=remaining_size,
            )
            
            await self.send_query({
                query_key: {
                    'chunk_payload': chunk_payload,
                },
            })
            
            result = await self.wait_for_result()
            result_data = getattr(result, result_key, None)
            assert_or_throw_invalid_result(result_data)
            
            chunk_ack = getattr(result_data, 'chunk_ack', None)
            assert_or_throw_invalid_result(chunk_ack)
            assert_or_throw_invalid_result(chunk_ack.chunk_index == i)






