use obi::{OBIDecode, OBIEncode, OBISchema};
use owasm_kit::{execute_entry_point, ext, oei, prepare_entry_point};
use strum_macros::Display;
use std::collections::hash_map::*;
use std::collections::HashMap;
use std::str::FromStr;
use strum::{EnumProperty, IntoEnumIterator, ParseError};
use strum_macros::{EnumIter, EnumProperty as EnumPropertyTrait, EnumString};

#[derive(OBIDecode, OBISchema)]
struct Input {
  symbols: Vec<String>,
  multiplier: u64,
}

#[derive(OBIEncode, OBISchema)]
struct Output {
  rates: Vec<u64>,
}

const EXCHANGE_COUNT: u64 = 18;

// Add non CCXT data source to this array
const API_SOURCE: [Exchange; 5] = [
  Exchange::CRYPTOCOMPARE,
  Exchange::COINGECKO,
  Exchange::COINBASEPRO,
  Exchange::COINMARKETCAP,
  Exchange::BRAVENEWCOIN,
];

#[derive(Display, EnumString, EnumIter, PartialEq, Debug, Copy, Clone)]
enum Token {
    ATOM,
    OSMO,
    SCRT,
    AKT,
    UST,
    JUNO,
    CRO,
    ION,
    XPRT,
    DVPN,
    LUNA,
    REGEN,
    KRT,
    IRIS,
    IOV,
    NGM,
    IXO,
    BCNA,
    BTSG,
    XKI,
    LIKE,
    EEUR,
    BAND,
    CMDX,
    TICK,
    MED ,
    CHEQ,
    STARS,
    HUAHUA,
    LUM,
    VDL,
    DSM,
    XAG,
    XAU,
    OIL,
}

// Special cases for Tokens starting with number that cannot be directly assigned to enum
impl Token {
  fn to_token_string(self: Token) -> String {
    match self {
      _ => self.to_string(),
    }
  }
  fn from_token_string(symbol: &str) -> Result<Token, ParseError> {
    match symbol {
      _ => Token::from_str(symbol),
    }
  }
}

#[derive(Display, EnumString, EnumIter, EnumPropertyTrait, Debug, Copy, Clone, PartialEq)]
enum Exchange {
  #[strum(props(data_source_id = "383"))]
  COINGECKO = 0,
  #[strum(props(data_source_id = "255"))]
  CRYPTOCOMPARE = 1,
  #[strum(props(data_source_id = "208"))]
  BRAVENEWCOIN = 2,
  #[strum(props(data_source_id = "236"))]
  COINMARKETCAP = 3,
  BINANCE = 4,
  HUOBIPRO = 5,
  #[strum(props(data_source_id = "119"))]
  COINBASEPRO = 6,
  KRAKEN = 7,
  BITFINEX = 8,
  BITTREX = 9,
  BITSTAMP = 10,
  OKEX = 11,
  FTX = 12,
  HITBTC = 13,
  ITBIT = 14,
  BITHUMB = 15,
  COINONE = 16,
  BIBOX = 17,
}

impl Exchange {
  fn from_u64(value: u64) -> Option<Exchange> {
    Exchange::iter().nth(value as usize)
  }
}

macro_rules! token_to_exchange_list {
  ($data:expr) => {
    match $data {
      Token ::ATOM    =>  "110100000000000000",
      Token ::OSMO    =>  "110100000000000000",
      Token ::SCRT    =>  "110100000000000000",
      Token ::AKT     =>  "110000000000000000",
      Token ::UST     =>  "110000000000000000",
      Token ::JUNO    =>  "100000000000000000",
      Token ::CRO     =>  "110100000000000000",
      Token ::ION     =>  "100000000000000000",
      Token ::XPRT    =>  "110000000000000000",
      Token ::DVPN    =>  "110000000000000000",
      Token ::LUNA    =>  "110000000000000000",
      Token ::REGEN   =>  "100000000000000000",
      Token ::KRT     =>  "100000000000000000",
      Token ::IRIS    =>  "110000000000000000",
      Token ::IOV     =>  "100000000000000000",
      Token ::NGM     =>  "100000000000000000",
      Token ::IXO     =>  "100000000000000000",
      Token ::BCNA    =>  "100000000000000000",
      Token ::BTSG    =>  "100000000000000000",
      Token ::XKI     =>  "100000000000000000",
      Token ::LIKE    =>  "100000000000000000",
      Token ::EEUR    =>  "100000000000000000",
      Token ::BAND    =>  "100100000000000000",
      Token ::CMDX    =>  "100000000000000000",
      Token ::TICK    =>  "100000000000000000",
      Token ::MED     =>  "100000000000000000",
      Token ::CHEQ    =>  "100000000000000000",
      Token ::STARS   =>  "100000000000000000",
      Token ::HUAHUA  =>  "100000000000000000",
      Token ::LUM     =>  "100000000000000000",
      Token ::VDL     =>  "100000000000000000",
      Token ::DSM     =>  "100000000000000000",
      Token ::XAG     =>  "100000000000000000",
      Token ::XAU     =>  "100000000000000000",
      Token ::OIL     =>  "100000000000000000",
      _=>"100000000000000000"
    }
};
}

fn get_ds_input(symbols: Vec<Token>) -> String {
    format!(
      "{}",
      symbols
        .iter()
        .map(|&x| x.to_token_string())
        .collect::<Vec<_>>()
        .join(" ")
    )
}

fn get_ds_from_exchange(exchange_id: u64) -> i64 {
  let exchange = match Exchange::from_u64(exchange_id) {
    Some(data) => data,
    None => panic!("Unsupported Exchange ID"),
  };
  if API_SOURCE.contains(&exchange) {
    i64::from_str(exchange.get_str("data_source_id").unwrap()).unwrap()
  } else {
    207i64 // CCXT Data source id
  }
}

fn get_symbols_from_input(exchange_id: u64, input: String) -> Vec<String> {
  let exchange = Exchange::from_u64(exchange_id).unwrap();
  if API_SOURCE.contains(&exchange) {
    input.split(" ").map(|x| x.to_string()).collect()
  } else {
    let mut v: Vec<String> = input.split(" ").map(|x| x.to_string()).collect();
    v.drain(0..1);
    v
  }
}
/*
0 -> atom,cmdx
1-> atom
*/
// Get list of exchange that needs to be called along with the symbols to call
// given a list of input symbols
fn get_exchange_map(symbols: Vec<String>) -> HashMap<u64, Vec<Token>> {
  let mut exchange_map = HashMap::new();
  for symbol in symbols {
    let symbol_token = Token::from_token_string(symbol.as_str()).unwrap();
    let mut exchange_binary = token_to_exchange_list!(symbol_token).chars();
    for i in 0..(EXCHANGE_COUNT as usize) {
      if exchange_binary.next() == Some('1') {
        match exchange_map.entry(i as u64) {
          Entry::Vacant(e) => {
            e.insert(vec![symbol_token]);
          }
          Entry::Occupied(mut e) => {
            e.get_mut().push(symbol_token);
          }
        }
      }
    }
  }
  exchange_map
}

fn median(arr: &mut Vec<f64>) -> f64 {
  let len_arr = arr.len() as f64;
  if len_arr > 0f64 {
    arr.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let mid = len_arr / 2f64;
    if len_arr as u64 % 2 == 0 {
      (arr[(mid - 1f64) as usize] + arr[mid as usize]) / 2f64
    } else {
      arr[mid as usize]
    }
  } else {
    0f64
  }
}

fn prepare_impl(input: Input) {
  //for a given exchange id get the list of tokens 
  let exchange_map = get_exchange_map(input.symbols);
  for (exchange_id, symbols) in exchange_map.iter() {
    oei::ask_external_data(
      *exchange_id as i64,
      get_ds_from_exchange(*exchange_id),
      get_ds_input( symbols.to_vec()).as_bytes(),
    )
  }
}

#[no_mangle]
fn execute_impl(input: Input) -> Output {
  // Get the required exchange and associated symbols to query
  let exchange_map = get_exchange_map((*input.symbols).to_vec());
  // store the median price of each token requested from an exchange
  let mut exchange_medians: Vec<Option<Vec<f64>>> = vec![Some(vec![]); EXCHANGE_COUNT as usize];
  for (exchange_id, _symbols) in exchange_map.iter() {
    // Get the data source calldata for a given external ID
    let raw_input = ext::load_input::<String>(*exchange_id as i64);
    let mut prices = vec![vec![]; exchange_map[exchange_id].len()];
    let inputs: Vec<String> = raw_input.collect();
    if inputs.len() == 0 {
      exchange_medians[*exchange_id as usize] = None;
      continue;
    }
    // for each validator response for the exchange,
    // split the response into individual prices
    for raw in inputs {
      let px_list: Vec<f64> = raw
        .split(",")
        .filter_map(|x| x.parse::<f64>().ok())
        .collect();
      // for each token price, add it to the list of validator responses
      // for that token and exchange
      for (idx, &px) in px_list.iter().enumerate() {
        prices[idx].push(px);
      }
    }
    let mut median_prices = vec![0f64; prices.len()];
    for (idx, price) in prices.iter().enumerate() {
      median_prices[idx] = median(&mut price.to_vec());
    }
    exchange_medians[*exchange_id as usize] = Some(median_prices);
  }

  let mut symbol_pxs = HashMap::new();
  for (exchange_id, symbols) in exchange_map.iter() {
    let exchange_median = exchange_medians[*exchange_id as usize].as_ref();
    if exchange_median.is_none() {
      continue;
    }
    let exchange_median = exchange_median.unwrap();
    let symbols_vec =
      get_symbols_from_input(*exchange_id, get_ds_input(symbols.to_vec()));

    for (symbol_id, symbol) in symbols_vec.iter().enumerate() {
      match symbol_pxs.entry(symbol.clone()) {
        Entry::Vacant(e) => {
          e.insert(vec![exchange_median[symbol_id]]);
        }
        Entry::Occupied(mut e) => {
          e.get_mut().push(exchange_median[symbol_id]);
        }
      }
    }
  }

  let mut rates = Vec::new();
  for symbol in input.symbols.iter() {
    rates.push((median(symbol_pxs.get_mut(*&symbol).unwrap()) * (input.multiplier as f64)) as u64)
  }
  Output { rates }
}

prepare_entry_point!(prepare_impl);
execute_entry_point!(execute_impl);
