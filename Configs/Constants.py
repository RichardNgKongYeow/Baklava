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