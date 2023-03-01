from utils import *
import txFields
import rxFields


class GBT_SCA:
    def __init__(self, transport):
        # the stuff we need to do to init everything
        pass

    def encode(self, message: dict) -> bytearray:
        """
        Arguments:
          bst_address   : Broadcast Address. Each bit corresponds of 1/40 SCAs; 40 bits
          repl_address   : Reply Address of the SCA. 0x7 corresponds to SCA 8/40; 6 bits
          cmd_id        : Command id; 3 bits
          sca_address   : SCA address; 8 bits
          trans_id      : Transaction id; 8 bits
          ch_address    : SCA channel address; 8 bits
          cmd           : Command; 8 bits
          payload       : entries to write; between zero and 4 bytes
        Output: list of 4 32-bit words
        """

        out = (message['bst_address'] &
               txFields.BROADCAST_ADDR_MASK) << txFields.BROADCAST_ADDR_OFFSET
        out = out | ((message['repl_address'] &
                     txFields.REPLY_ADDR_MASK) << txFields.REPLY_ADDR_OFFSET)
        out = out | ((message['cmd_id'] & txFields.COMMAND_ID_MASK)
                     << txFields.COMMAND_ID_OFFSET)
        out = out | ((message['sca_address'] &
                     txFields.SCA_ADDR_MASK) << txFields.SCA_ADDR_OFFSET)
        out = out | (
            (message['trans_id'] & txFields.TRANSACTION_ID_MASK) << txFields.TRANSACTION_ID_OFFSET)
        out = out | (
            (message['ch_address'] & txFields.CHANNEL_ADDR_MASK) << txFields.CHANNEL_ADDR_OFFSET)
        out = out | ((message['cmd'] & txFields.COMMAND_MASK)
                     << txFields.COMMAND_OFFSET)
        out = out | (
            (message['payload'] & txFields.PAYLOAD_MASK) << txFields.PAYLOAD_OFFSET)

        data = [(out >> i*32) & 0xFFFFFFFF for i in range(4)]

        return data

    @staticmethod
    def _tx_decode(data: bytearray) -> dict:
        """
          decoded_data: dict with fields values
          only needed for debugging purposes
        """
        bst_address = (data[3] << 8)
        bst_address += (data[2] >> (txFields.BROADCAST_ADDR_OFFSET % 32))
        repl_address = (data[2] >> (
            txFields.REPLY_ADDR_OFFSET % 32)) & txFields.REPLY_ADDR_MASK
        cmd_id = (data[2] >> (
            txFields.COMMAND_ID_OFFSET % 32)) & txFields.COMMAND_ID_MASK
        sca_address = (data[1] >> (
            txFields.SCA_ADDR_OFFSET % 32)) & txFields.SCA_ADDR_MASK
        trans_id = (data[1] >> (
            txFields.TRANSACTION_ID_OFFSET % 32)) & txFields.TRANSACTION_ID_MASK
        ch_address = (data[1] >> (
            txFields.CHANNEL_ADDR_OFFSET % 32)) & txFields.CHANNEL_ADDR_MASK
        cmd = (data[1] >> (txFields.COMMAND_OFFSET %
               32)) & txFields.COMMAND_MASK
        payload = data[0]

        fields_dict = {'bst_address': bst_address, 'repl_address': repl_address, 'cmd_id': cmd_id,
                       'sca_address': sca_address, 'trans_id': trans_id, 'ch_address': ch_address,
                       'cmd': cmd, 'payload': payload}
        return fields_dict

    @staticmethod
    def decode(data: bytearray) -> dict:
        """
        Output: dictionary containing the fields:
          error_flag    : SCA error flags written in RX buffer when transaction fails; 3 bits
          sca_address   : SCA address; 8 bits
          ctrl          : Frame sequence numbers of the currently transmitted 
                          frame and the last correctly received frame; 8 bits
          trans_id      : Message identification number.; 8 bits
          ch_address    : Destination interface of the request message; 8 bits
          nbytes        : Number of bytes contained in the payload field; 8 bits
          error         : Error conditions encountered in the execution of a command; 8 bits
          payload       : entries to write; between zero and 4 bytes
          Output        : dict with fields values
        """

        if len(data) != 4:
            raise ValueError(
                'encoded data should be a list of 4 32-bits words')
        bit_length_error = [blen(d) > 32 for d in data]
        if True in bit_length_error:
            raise ValueError(
                'at least 1 word in encoded data is more than 32-bits')

        error_flag = ((data[2]) >> (
            rxFields.ERROR_FLAGS_OFFSET % 32)) & rxFields.ERROR_FLAGS_MASK
        sca_address = ((data[2]) >> (
            rxFields.SCA_ADDR_OFFSET % 32)) & rxFields.SCA_ADDR_MASK
        ctrl = ((data[2]) >> (
            rxFields.CONTROL_OFFSET % 32)) & rxFields.CONTROL_MASK
        trans_id = ((data[1]) >> (
            rxFields.TRANSACTION_ID_OFFSET % 32)) & rxFields.TRANSACTION_ID_MASK
        ch_address = ((data[1]) >> (
            rxFields.CHANNEL_ADDR_OFFSET % 32)) & rxFields.CHANNEL_ADDR_MASK
        nbytes = ((data[1]) >> (
            rxFields.NBYTES_PAYLOAD_OFFSET % 32)) & rxFields.NBYTES_PAYLOAD_MASK
        error = (data[1] >> (
            rxFields.ERROR_OFFSET % 32)) & rxFields.ERROR_MASK
        payload = data[0]

        fields_dict = {'error_flag': error_flag,
                       'sca_address': sca_address,
                       'ctrl': ctrl,
                       'trans_id': trans_id,
                       'ch_address': ch_address,
                       'nbytes': nbytes,
                       'error': error,
                       'payload': payload
                       }

        return fields_dict

    def _rx_encode(self, message: dict) -> bytearray:
        """
          encoded_data: list of 4 32-bits words
          only needed for debugging purposes
        """
        out = (message['error_flag'] &
               rxFields.ERROR_FLAGS_MASK) << rxFields.ERROR_FLAGS_OFFSET
        out = out | (
            (message['sca_address'] & rxFields.SCA_ADDR_MASK) << rxFields.SCA_ADDR_OFFSET)
        out = out | ((message['ctrl'] & rxFields.CONTROL_MASK)
                     << rxFields.CONTROL_OFFSET)
        out = out | ((message['trans_id'] & rxFields.TRANSACTION_ID_MASK)
                     << rxFields.TRANSACTION_ID_OFFSET)
        out = out | (
            (message['ch_address'] & rxFields.CHANNEL_ADDR_MASK) << rxFields.CHANNEL_ADDR_OFFSET)
        out = out | ((message['nbytes'] & rxFields.NBYTES_PAYLOAD_MASK)
                     << rxFields.NBYTES_PAYLOAD_OFFSET)
        out = out | ((message['error'] & rxFields.ERROR_MASK)
                     << rxFields.ERROR_OFFSET)
        out = out | (
            (message['payload'] & rxFields.PAYLOAD_MASK) << rxFields.PAYLOAD_OFFSET)

        data = [(out >> i*32) & 0xFFFFFFFF for i in range(4)]

        return data
