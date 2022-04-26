TODO:
    - calculate total gamma
    - weigh net gamma against ratio of OI/volume
        - sense of dealer vs non-dealer on intraday
        - ie, correlation of OI/volume vs net gamma day to day
        - later, test against intraday performance



data storage
    - each contract identified by expiry + strike
    - top level: expiry dates
    - next level: strike price
    - next level: range of timestamps each strike (timestamps of when data was collected)
    - final level: bid/ask, greeks, etc.


don't need to store anything yet i think (at least beyond a week's worth of data)
hierarchy:
session object
Fin object --> call on ticker(SPX or SPY) to pull all chain data
    - organize -> upload to gcloud
