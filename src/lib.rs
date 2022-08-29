use obi::{OBIDecode, OBIEncode, OBISchema};
use owasm_kit::{execute_entry_point, ext, oei, prepare_entry_point};

#[derive(OBIDecode, OBISchema)]
struct Input {
    symbols: Vec<String>,
}

#[derive(OBIEncode, OBISchema)]
struct Output {
    price: Vec<u64>,
}

const DATA_SOURCE_ID: i64 = 383;
const EXTERNAL_ID: i64 = 0;

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

#[no_mangle]
fn prepare_impl(input: Input) {
    oei::ask_external_data(
        EXTERNAL_ID,
        DATA_SOURCE_ID,
        input.symbols.join(",").as_bytes(),
    );
}

#[no_mangle]
fn execute_impl(input: Input) -> Output {
    let raw_input = ext::load_input::<String>(EXTERNAL_ID);
    let mut mean_medians = vec![0f64; input.symbols.len()];

    for iter_item in raw_input {
        // Split the various median prices received from data source.
        let ans: Vec<&str> = iter_item.split(",").collect();
        // Parse string to f64
        let prices: Vec<f64> = ans
            .into_iter()
            .filter_map(|el| el.parse::<f64>().ok())
            .collect();
        // Add the token price to respective index in mean_medians.
        for (index, price) in prices.into_iter().enumerate() {
            mean_medians[index] += price;
        }
    }

    // Calculate the mean and return the result
    Output {
        price: mean_medians
            .into_iter()
            .map(|el| (el / (input.symbols.len() as f64)) as u64)
            .collect(),
    }
}

prepare_entry_point!(prepare_impl);
execute_entry_point!(execute_impl);
