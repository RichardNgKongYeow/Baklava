from core.api_throttler.data_types import LinkedLimitWeightPair, RateLimit
from core.data_type.common import PositionSide, TradeType
from core.data_type.in_flight_order import OrderState
from core.event.events import PositionAction
import os

EXCHANGE_NAME = "fx_dex"

"""Domain - parameter passed to FxDexDerivative constructor"""
DOMAIN = EXCHANGE_NAME              # Mainnet
TESTNET_DOMAIN = "fx_dex_testnet"   # Testnet


"""Default parameters"""
TRADING_PAIR = os.environ.get("TRADING_PAIR", "BTC-USDT")
BASE_ASSET, QUOTE_ASSET = TRADING_PAIR.split("-")


"""Web URL (for orderbook snapshots and diffs)"""
H5_PERPETUAL_BASE_URL = "trade.marginx.io"
H5_TESTNET_BASE_URL = "trade.testnet.marginx.io"

# REST endpoint
PERPETUAL_BASE_URL = f"https://{H5_PERPETUAL_BASE_URL}/dex/common"
TESTNET_BASE_URL = f"https://{H5_TESTNET_BASE_URL}/dex/common"

# WebSockets
PERPETUAL_ORDERBOOK_WS_URL = f"wss://{H5_PERPETUAL_BASE_URL}/ws/websocket"
TESTNET_ORDERBOOK_WS_URL = f"wss://{H5_TESTNET_BASE_URL}/ws/websocket"


"""Chain endpoints (Tendermint)"""
# GRPC
PERPETUAL_GRPC_URL_FORMAT = "https://{}-grpc.marginx.io"
TESTNET_GRPC_URL_FORMAT = "https://testnet-{}-grpc-intranet.marginx.io"

# WebSockets
PERPETUAL_WS_URL_FORMAT = "wss://{}-json.marginx.io/"
TESTNET_WS_URL_FORMAT = "wss://testnet-{}-json-intranet.marginx.io/"

# Internal orderbook URL
INTERNAL_ORDERBOOK_URL = "http://{}-syncer-openapi-intranet.marginx.io/orderbook"

# Placeholder, filled in during FxDexDerivative initalization
GRPC_URL = ""
WS_URL = ""


"""Funding Settlement Time Span"""
FUNDING_SETTLEMENT_DURATION = (0, 30)  # seconds before snapshot, seconds after snapshot


"""Order Status Map"""
# https://wokoworks.feishu.cn/wiki/wikcnKXuJhixZh1evDgted6eOof
ORDER_STATE = {
    # From websocket
    "ORDER_PENDING": OrderState.OPEN,
    "ORDER_FILLED": OrderState.FILLED,
    "ORDER_PARTIAL_FILLED": OrderState.PARTIALLY_FILLED,
    "ORDER_CANCELLED": OrderState.CANCELLED,
    "ORDER_PARTIAL_FILLED_CANCELLED": OrderState.CANCELLED,
    "ORDER_PARTIAL_FILLED_EXPIRED": OrderState.CANCELLED,
    "ORDER_EXPIRED": OrderState.CANCELLED,
    "ORDER_GASOUT": OrderState.CANCELLED,       # order partially filled, but ran out of gas
    "ORDER_PRICE_LIMIT": OrderState.CANCELLED,  # order has consumed up to 20% price deviation; remainder cancelled

    # From GRPC
    0: OrderState.OPEN,
    1: OrderState.FILLED,
    2: OrderState.PARTIALLY_FILLED,
    3: OrderState.CANCELLED,
    4: OrderState.CANCELLED,
    5: OrderState.CANCELLED,
    6: OrderState.CANCELLED,
    7: OrderState.CANCELLED,
    8: OrderState.CANCELLED,
}


"""Map (FX Dex) Order Type to (Hummingbot) PositionAction"""
POSITION_ACTION = {
    # From websocket
    "ORDER_TYPE_OPEN_POSITION": PositionAction.OPEN,
    "ORDER_TYPE_CLOSE_POSITION": PositionAction.CLOSE,
    "ORDER_TYPE_LIQUIDATION": PositionAction.NIL,

    # From GRPC
    0: PositionAction.OPEN,
    1: PositionAction.CLOSE,
    2: PositionAction.NIL,
}

POSITION_SIDE = {
    # From GRPC
    0: PositionSide.BOTH,
    1: PositionSide.LONG,
    2: PositionSide.SHORT,

    "BOTH": PositionSide.BOTH,
    "LONG": PositionSide.LONG,
    "SHORT": PositionSide.SHORT,

    "both": PositionSide.BOTH,
    "long": PositionSide.LONG,
    "short": PositionSide.SHORT,
}

ORDER_DIRECTION = {
    # From websocket
    "BOTH": TradeType.RANGE,
    "BUY": TradeType.BUY,
    "SELL": TradeType.SELL,
    "MarketBuy": TradeType.BUY,
    "MarketSell": TradeType.SELL,

    # From GRPC
    0: TradeType.RANGE,     # BOTH
    1: TradeType.BUY,       # BUY
    2: TradeType.SELL,      # SELL
    3: TradeType.BUY,       # MarketBuy
    4: TradeType.SELL,      # MarketSell
}

"""Port mappings"""
GRPC_PORT_MAP = {
    "BTC":  9090,
    "ETH":  9190,
    "FX":   9290,
    "DOGE": 9390,
    "APE":  9490,
}

JSON_RPC_PORT_MAP = {
    "BTC":  21657,
    "ETH":  22657,
    "FX":   23657,
    "DOGE": 24657,
    "APE":  25657,
}

TESTNET_GRPC_PORT_MAP = {
    # "AAPL": 9090,
    # "AMZN": 9190,
    # "BTC":  9290,
    # "FB":   9390,
    # "FX":   9490,
    # "GOOG": 9590,
    # "IWM":  9090,
    # "NFLX": 9190,
    # "SPY":  9290,
    # "TQQQ": 9390,
    # "TSLA": 9490,
    "AAPL": 9090,
    "BTC": 9190,
    "FX": 9290,
    "TSLA": 9390,
}

TESTNET_JSON_RPC_PORT_MAP = {
    # "AAPL": 21657,
    # "AMZN": 22657,
    # "BTC":  23657,
    # "FB":   24657,
    # "FX":   25657,
    # "GOOG": 26657,
    # "IWM":  21657,
    # "NFLX": 22657,
    # "SPY":  23657,
    # "TQQQ": 24657,
    # "TSLA": 25657,
    "AAPL": 21657,
    "BTC": 22657,
    "FX": 23657,
    "TSLA": 24657,
}

DEVNET_GRPC_PORT_MAP = {
    "BTC":  9190,
    "TSLA": 9290,
}

DEVNET_JSON_RPC_PORT_MAP = {
    "BTC":  21657,
    "TSLA": 22657,
}

# https://wokoworks.feishu.cn/wiki/wikcngCl33JKbDVW4XPYy99sHJf
FATAL_ERROR_CODES = {
    5,      # insufficient funds
    7,      # invalid wallet address
    8,      # invalid public key
    10,     # invalid token
    11,     # insufficient funds for gas fee
    13,     # insufficient funds for tx fee
    19,     # tx already in mempool
    21,     # tx too large
    28,     # invalid chain id
    103,    # invalid price
    104,    # invalid base asset qty
    105,    # invalid direction
    106,    # order not found (cancelled or deleted)
    107,    # position not found
    108,    # invalid leverage
    109,    # decreasing leverage not supported
    110,    # insufficient position amount to close
    111,    # need to provide position closing amount
    112,    # position too large
    114,    # price too small
    115,    # price exceeds 20% limit
    116,    # permission denied
    117,    # position too small
    201,    # wrong coin
    203,    # invalid position id
    208,    # too many orders on one trading pair
    209,    # orderbook has insufficient orders
    210,    # module account net loss
    211,    # position is pending liquidation
}

STOCK_PAIRS = ["TSLA-USDT", "AAPL-USDT", "NFLX-USDT", "GOOG-USDT", "FB-USDT", "AMZN-USDT", "SPY-USDT", "IWM-USDT", "TQQQ-USDT"]
CRYPTO_PAIRS = ["APE-USDT", "BTC-USDT", "ETH-USDT", "FX-USDT"]

API_VERSION = "v1"

# REST endpoints
TRADES_URL = "/queryTrades"
ORDER_BOOK_URL = "/queryOrderBook"

# Rate Limit Type
REQUEST_WEIGHT = "REQUEST_WEIGHT"
ORDERS_1MIN = "ORDERS_1MIN"
ORDERS_1SEC = "ORDERS_1SEC"

# Stream IDs
TX_ID = 1
NEW_BLOCK_ID = 2
DIFF_STREAM_ID = 3
FUNDING_INFO_STREAM_ID = 4
TRADE_STREAM_ID = 5

# Websocket parameters
HEARTBEAT_TIME_INTERVAL = 15.0  # interval to send ping
WS_RETRY_INTERVAL = 1.0         # time to retry after WS closure

# Rate Limit time intervals
ONE_HOUR = 3600
ONE_MINUTE = 60
ONE_SECOND = 1
ONE_DAY = 86400

MAX_REQUEST = 2400

RATE_LIMITS = [
    # Pool Limits
    RateLimit(limit_id=REQUEST_WEIGHT, limit=2400, time_interval=ONE_MINUTE),
    RateLimit(limit_id=ORDERS_1MIN, limit=1200, time_interval=ONE_MINUTE),
    RateLimit(limit_id=ORDERS_1SEC, limit=300, time_interval=10),
    # Weight Limits for individual endpoints
    RateLimit(limit_id=TRADES_URL, limit=MAX_REQUEST, time_interval=ONE_MINUTE,
              linked_limits=[LinkedLimitWeightPair(REQUEST_WEIGHT, weight=20)]),
]

class GasDenom:
    """Utility class for TxBuilder gas_price parameter"""
    FX = "FX"
    USDT = "USDT"
