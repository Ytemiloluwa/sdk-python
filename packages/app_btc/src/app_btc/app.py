from interfaces import IDeviceConnection
from core.sdk import SDK
from . import operations


class BtcApp:
    """
    Bitcoin application class for Cypherock SDK.
    """
    
    APPLET_ID = 2
    
    def __init__(self, sdk: SDK):
        """
        Private constructor. Use create() class method instead.
        
        Args:
            sdk: SDK instance
        """
        self._sdk = sdk
    
    @classmethod
    async def create(cls, connection: IDeviceConnection) -> 'BtcApp':
        """
        Create a new BtcApp instance.
        
        Args:
            connection: Device connection instance
            
        Returns:
            BtcApp instance
        """
        sdk = await SDK.create(connection, cls.APPLET_ID)
        return cls(sdk)
    
    async def get_public_key(self, params: operations.GetPublicKeyParams) -> operations.GetPublicKeyResult:
        """
        Get public key and address from device.
        
        Args:
            params: Parameters for getting public key
            
        Returns:
            Public key and address result
        """
        return await self._sdk.run_operation(
            lambda: operations.get_public_key(self._sdk, params)
        )
    
    async def get_xpubs(self, params: operations.GetXpubsParams) -> operations.GetXpubsResultResponse:
        """
        Get extended public keys from device.
        
        Args:
            params: Parameters for getting xpubs
            
        Returns:
            Extended public keys result
        """
        return await self._sdk.run_operation(
            lambda: operations.get_xpubs(self._sdk, params)
        )
    
    async def sign_txn(self, params: operations.SignTxnParams) -> operations.SignTxnResult:
        """
        Sign Bitcoin transaction on device.
        
        Args:
            params: Parameters for signing transaction
            
        Returns:
            Signed transaction result
        """
        return await self._sdk.run_operation(
            lambda: operations.sign_txn(self._sdk, params)
        )
    
    async def destroy(self) -> None:
        """
        Destroy the SDK instance and cleanup resources.
        """
        return await self._sdk.destroy()
    
    async def abort(self) -> None:
        """
        Send abort signal to device.
        """
        await self._sdk.send_abort()

