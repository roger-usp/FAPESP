function fill_selectbox(select_element, values, contents){
    let num_options = values.length;
    let options = "";
    for (let i=0; i<num_options; i++) {
        let option_tag = '<option value="'+ String(values[i]) + '">' + String(contents[i]) + '</option>';
        options += option_tag
    }
    select_element.innerHTML = options
};

async function fill_feedstock_type_selectbox(){
    let selectbox = await document.getElementById("feedstock_type_selectbox");
    let response = await fetch("../feedstock_types");
    let data = await response.json()
    let values = await data.feedstock_type_id
    let contents = await data.feedstock_type
    await fill_selectbox(selectbox, values, contents);
};
/*
function feedstock_type_changed(){
    return
};

function feedstock_changed(){
    return
};
*/