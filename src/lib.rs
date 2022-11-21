use obi::{OBIDecode, OBIEncode, OBISchema};
use owasm_kit::{execute_entry_point, ext, oei, prepare_entry_point};

#[derive(OBIDecode, OBISchema)]
struct Input {
    symbols: Vec<String>,
    multiplier: u64,
}

#[derive(OBIEncode, OBISchema)]
struct Output {
    rates: Vec<u64>,
}

const DATA_SOURCE_ID: [i64; 1] = [504];
const EXTERNAL_ID: [i64; 1] = [0];

#[no_mangle]
fn prepare_impl(input: Input) {
    let inputs_dup = input.symbols.clone();
    oei::ask_external_data(
        EXTERNAL_ID[0],
        DATA_SOURCE_ID[0],
        inputs_dup.join(" ").as_bytes()
    )
}

fn except_zero(arr:&mut Vec<f64>)->f64{
  let len=arr.len() as f64;
  let d:usize=len as usize;
  let mut i:usize=0;
  let mut c:f64=0.0;
  for j in 0..d{
     if arr[j]==0.0
     {
       i=i+1;
     }
     c=c+arr[j];
  }
  let f=(d-i) as f64;
  if i==d{
  return 0.0;
  }
  else{
    c/f
  }  
}

#[no_mangle]
fn execute_impl(_input: Input) -> Output {
  let mut _exchange_medians:Option<Vec<f64>> = Some(vec![]);
  let raw_input = ext::load_input::<String>(EXTERNAL_ID[0]);
  let mut prices: Vec<Vec<f64>> = vec![vec![]; _input.symbols.len()];
  let inputs:Vec<String> = raw_input.collect();  
  if inputs.is_empty(){
    _exchange_medians = None;  
  } else {
    for raw in inputs{
      let validator_price_list:Vec<f64> = raw
      .split(',')
      .filter_map(|x| x.parse::<f64>().ok())
      .collect(); 

      for (index,&price) in validator_price_list.iter().enumerate() {
        prices[index].push(price);
      }
    }     
    let mut median_prices = vec![0f64; _input.symbols.len()];
    for (idx,price) in prices.iter().enumerate(){
      median_prices[idx]=except_zero(&mut price.to_vec());
    }
    _exchange_medians = Some(median_prices);
  }
  let mut rates:Vec<u64> = Vec::new();
  if _exchange_medians.is_some() {
    let exchange_medians = _exchange_medians.unwrap();
    for item in &exchange_medians {
      rates.push(((*item)*(_input.multiplier as f64)) as u64);
    }
  }
  Output { rates: rates }
}

prepare_entry_point!(prepare_impl);
execute_entry_point!(execute_impl);
