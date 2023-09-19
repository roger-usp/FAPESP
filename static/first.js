async function fill_feedstock_selectbox(){
    let url = "../feedstocks";
    let response = await fetch(url);
    let result = await response.json();
    let values = result.feedstock_id;
    let contents = result.feedstock_name;
    let num_feedstocks = values.length;
    let feedstock_selectbox = document.getElementById("feedstock_selectbox");
    let options = '<option value="" disabled selected hidden>Selecione</option>';
    for (let i = 0; i<num_feedstocks; i++){
        options += `<option value=${values[i]}>${contents[i]}</option>`;
    };
    feedstock_selectbox.innerHTML = options;
    console.log(options)
}

async function fill_year_selectbox(feedstock_id){
    let url = "../years/" + String(feedstock_id);
    let response = await fetch(url);
    let result = await response.json();
    let num_years = result.length;
    let options = '<option value="" disabled selected hidden>Selecione</option>'
    for (let i = 0; i<num_years; i++){
        options += `<option value=${result[i]}>${result[i]}</option>`;
    };
    let year_selectbox = document.getElementById("year_selectbox");
    year_selectbox.innerHTML = options;
}

function fill_region_type_selectbox(){
    let region_types = {
        "values": ["uf", "inter", "imed", "mun"],
        "contents": ["Estados", "Regiões Intermediárias", "Regiões Imediatas", "Municípios"]
    };
    let options = '<option value="" disabled selected hidden>Selecione</option>';
    for (let i = 0; i<4;i++){
        options += `<option value=${region_types.values[i]}>${region_types.contents[i]}</option>`;
    };
    let region_type_selectbox = document.getElementById("region_type_selectbox");
    region_type_selectbox.innerHTML = options;
}

async function feedstock_changed(){
    let feedstock_id = document.getElementById("feedstock_selectbox").value;
    fill_year_selectbox(feedstock_id);
    
}

function get_max_production(geojson){
    let features = geojson.features;
    let num_features = features.length;
    let production = [];
    for (let i=0; i<num_features; i++){
        production.push(features[i].properties.quantity_produced);
    };
    let max_production = Math.max(...production);
    return max_production
}

function make_get_color(max){
return function getColor(d) {
        return d < max/7 ? '#FFEDA0' :
           d < 2*max/7  ? '#FEB24C' :
           d < 3*max/7  ? '#FD8D3C' :
           d < 4*max/7  ? '#FC4E2A' :
           d < 5*max/7  ? '#E31A1C' :
           d < 6*max/7  ? '#BD0026' :
                          '#800026';
}}


function show_info(e) {
    var layer = e.target;
    let quantity_produced = layer.feature.properties.quantity_produced;
    quantity_produced = quantity_produced.toLocaleString('pt-BR');
    let region_name = layer.feature.properties.name;
    let region_code = layer.feature.properties.id;
    let population = layer.feature.properties.population.toLocaleString('pt-BR');
    let popup_string = `Produção: ${quantity_produced} ton/ano<br>Código IBGE: ${region_code}<br>Nome: ${region_name}<br>População: ${population} hab`
    layer.bindPopup(popup_string).openPopup();
    layer.bringToFront();
}

function hide_info(e){
    var layer = e.target;
    layer.closePopup();
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: show_info,
        mouseout: hide_info,
    });
}

function make_map(geojson){
    var map = L.map('map').setView([-15.4451, -49.2037], 4);
    var tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    let max = get_max_production(geojson);
    let my_style = function style(feature) {
        return {
            fillColor: make_get_color(max)(feature.properties.quantity_produced),
            weight: 2,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
        };
    }
    
    L.geoJson(geojson, {style: my_style, onEachFeature: onEachFeature}).addTo(map);
    
}

async function update_map(){
    let feedstock_id = String(document.getElementById("feedstock_selectbox").value);
    let region_type = String(document.getElementById("region_type_selectbox").value);
    let year = String(document.getElementById("year_selectbox").value);
    if (feedstock_id === "" || region_type === "" || year === ""){
        window.alert("Selecione todas as opções")
    }

    let url = '../geojson/' + feedstock_id + '/' + region_type + '/' + year;
    let geojson = await fetch(url);
    geojson = await geojson.json();
    let map_div = document.getElementById("map_div");
    map_div.innerHTML = '<div id="map" style="height: 400px;"></div>';
    make_map(geojson);
}