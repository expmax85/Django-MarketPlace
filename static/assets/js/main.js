function PriceDiscount(valNum) {
    document.getElementById("id_discount").addEventListener("change", makeValue);
    let selectvalue = makeValue();
    document.querySelector("#id_price_after_discount").setAttribute("value", valNum - selectvalue);

    function makeValue() {
       let select = document.querySelector('#id_discount');
       let indexSelected = select.selectedIndex,
       option = select.querySelectorAll('option')[indexSelected];
       let selectedId = option.getAttribute('id');
       let result

       if (selectedId !== null) {
           result = selectedId.split('~')[1];
       } else {
           return 0;
       }
       if (isNaN(result)){
           selectedId = selectedId.split('~')[2];
           return selectedId;
       } else {
           return valNum * result / 100;
       }
    }
}

$(function(){
  $("#id_phone").mask("+7(999)999-99-99");
});

function ajaxSend(url, params) {
    // Отправляем запрос
    fetch(`${url}?${params}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => response.json())
        .then(json => render(json))
        .catch(error => console.error(error))
}

 const forms = document.querySelector('form[name=category-filter]');

 forms.addEventListener('submit', function (e) {
     // Получаем данные из формы
     e.preventDefault();
     let url = this.action;
     let params = new URLSearchParams(new FormData(this)).toString();
     ajaxSend(url, params);
 });

function render(data) {
    // Рендер шаблона
    let template = Hogan.compile(html);
    let output = template.render(data);

    const div = document.querySelector('#id_product');
    div.innerHTML = output;
}

let html = '\
<option value="" selected="">---------</option>\
{{#products}}\
    <option value="{{ id }}">{{ name }}</option>\
{{/products}}'