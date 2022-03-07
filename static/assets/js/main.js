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
function ajaxSend(url, params, render_data) {
    // Отправляем запрос
    fetch(`${url}?${params}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => response.json())
        .then(json => render(json, render_data))
        .catch(error => console.error(error))
}

function render(data, render_data) {
    // Рендер шаблона

    let template = Hogan.compile(render_data);
    let output = template.render(data);
    console.log(data)
    const div = document.querySelector('.product_js');
    div.innerHTML = output;
}

const form_filter = document.querySelector('form[name=json-filter]');
form_filter.addEventListener('submit', function(e) {
    // Получаем данные из формы
    e.preventDefault();
    let url = this.action;
    let params = new URLSearchParams(new FormData(this)).toString();
    ajaxSend(url, params, html_filter);
});

let html_filter = '\
<div class="Cards-wrap">\
{{#products}}\
<div class="Card"><a class="Card-picture" href="#"><img src="/uploads/{{ product__image }}" alt="card.jpg"></a>\
  <div class="Card-content">\
    <strong class="Card-title"><a href="/product-detail/{{ product__slug }}/">{{ product__name }}</a>\
    </strong>\
    <div class="Card-description">\
      <div class="Card-cost"><span class="Card-priceOld">{{ price }}</span><span class="Card-price">{{ price_after_discount }}</span>\
      </div>\
      <div class="Card-category">{{ product__category__name }}\
      </div>\
      <div class="Card-hover"><a class="Card-btn" href="#"><img src="/static/assets/img/icons/card/bookmark.svg" alt="bookmark.svg"></a><a class="Card-btn" href="/orders/add/{{ id }}/"><img src="/static/assets/img/icons/card/cart.svg" alt="cart.svg"></a><a class="Card-btn" href="/orders/compare/add/{{ id }}/"><img src="/static/assets/img/icons/card/change.svg" alt="change.svg"></a>\
      </div>\
    </div>\
      {{#discount__percent }}\
      <div class="Card-sale">-{{ discount__percent }}%\
      </div>\
      {{/discount__percent }}\
      {{#discount__amount }}\
      <div class="Card-sale">Hot deal\
      </div>\
      {{/discount__amount }}\
  </div>\
</div>\
{{/products}}\
</div>\
<button id="btn_page" class="btn btn_default btn_sm">\
<select id="id_page" name="page" multiple>\
{{#has_previous }}\
<option class="btn btn_default btn_sm" name="page" value="1">1</option>\
<option class="btn btn_default btn_sm" name="page" value="{{previous_page_number}}"><<</option>\
{{/has_previous }}\
<option class="btn btn_default btn_sm" name="page" value="{{number}}" selected>{{number}}</option>\
{{#has_next }}\
<option class="btn btn_default btn_sm" name="page" value="{{next_page_number}}">>></option>\
<option class="btn btn_default btn_sm" name="page" value="{{num_pages}}">{{num_pages}}</option>\
{{/has_next }}\
</select>\
</button>'

const forms = document.querySelector('form[name=category-filter]');
forms.addEventListener('submit', function (e) {
 // Получаем данные из формы
 e.preventDefault();
 let url = this.action;
 let params = new URLSearchParams(new FormData(this)).toString();
 ajaxSend2(url, params, html);
});

let html = '\
<option value="" selected="">---------</option>\
{{#products}}\
    <option value="{{ id }}">{{ name }}</option>\
{{/products}}'
