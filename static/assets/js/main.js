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

// Филтр
function ajaxSend(url, params, render_data, target) {
    // Отправляем запрос
    fetch(`${url}?${params}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => response.json())
        .then(json => render(json, render_data, target))
        .catch(error => console.error(error))
}

function render(data, render_data, target) {
    // Рендер шаблона

    let template = Hogan.compile(render_data);
    let output = template.render(data);
    target.innerHTML = output;
}

const target2 = document.querySelector('.product_js');
const forms = document.querySelector('form[name=category-filter]');
forms.addEventListener('click', function (e) {
 // Получаем данные из формы
 e.preventDefault();
 let url = this.action;
 let params = new URLSearchParams(new FormData(this)).toString();
 ajaxSend(url, params, html, target2);
});

let html = '\
<label class="form-label" for="id_product">Product:</label>\
<select class="form-area product-js" name="product" required="" id="id_product">\
  <option value="" selected="">---------</option>\
  {{#products}}\
  <option value="{{ id }}">{{ name }}</option>\
  {{/products}}\
</select>'


