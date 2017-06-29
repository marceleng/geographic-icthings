### 802.15.4 constants ###
HDR_802154_PHY = 6
HDR_802154_MAC = 23
HDR_802154_SEC = 5
HDR_802154_SIG = 16
HDR_802154_CRC = 2
HDR_802154_LEN = HDR_802154_PHY + HDR_802154_MAC + HDR_802154_SEC + HDR_802154_SIG + HDR_802154_CRC

### ICN constants ###
ICN_INT_HDR_LEN = 4 #PacketType TL + Nonce TLV + Name TL
ICN_CNT_SEC_LEN = 1 + 2 + 2 + 2 + 17 #SigInfo TL + SigType TLV + KeyLoc TLV + KeyId TLV + Sig TLV
ICN_CNT_HDR_LEN = 1 + 1 + 1 + ICN_CNT_SEC_LEN #PacketType TL + Name TL + Content TL + SigInfo TLV
ICN_GEO_TLV_HDR = 1 + 1 # GPSR TL + Flags

TOTAL_SECURITY_OVERHEAD = HDR_802154_SEC + HDR_802154_SIG + 1 +ICN_CNT_SEC_LEN

### Energy constants ###
AA_J = 15390
J_IN_UJ = 1000000.0
COST_RX_UJ=0.96
COST_TX_UJ=1.163
CPU_AMP=13./1000
CPU_FREQ=32*1000000
CRYPTO_UJ = 10

### Functions ###
def icn_int_frame_size (name_size):
    return HDR_802154_LEN + ICN_INT_HDR_LEN + name_size

def icn_geo_int_frame_size(name_size, sloc):
    return HDR_802154_LEN + ICN_GEO_TLV_HDR + ICN_INT_HDR_LEN + name_size + sloc #sloc if for the GPSR TLV

def icn_cnt_frame_size(name_size, content_size):
    return HDR_802154_LEN + ICN_CNT_HDR_LEN + name_size + content_size

def icn_int_packet_size (name_size):
    return ICN_INT_HDR_LEN + name_size

def icn_geo_int_packet_size(name_size, sloc):
    return ICN_GEO_TLV_HDR + ICN_INT_HDR_LEN + name_size + sloc #sloc if for the GPSR TLV

def icn_cnt_packet_size(name_size, content_size):
    return ICN_CNT_HDR_LEN + name_size + content_size

def max_trans_mess_energy(frame_size):
    return AA_J /(frame_size * (2*CRYPTO_UJ + COST_RX_UJ + COST_TX_UJ)/J_IN_UJ)
