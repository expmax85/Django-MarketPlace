function ajaxSend(url, params, render_data, target) {
    // Отправление запроса
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
    let month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    (data.comments).forEach(function(item){
        let date = new Date(item.added)
        item.added = month[date.getMonth()] + ' / ' + String(date.getDay()) + ' / ' + String(date.getFullYear()) + ' ' + String(date.getHours()) + ':' + String(date.getMinutes())
    })
    let output = template.render(data);
    target.innerHTML = output;
    let get = document.querySelectorAll('.count_reviews')
    get.forEach(function (item){
        item.innerHTML = data['reviews_count'].toString()
    })
}

const target = document.querySelector('.comments-js');
const forms = document.querySelector('form[name=page-filter]');
forms.addEventListener('click', function (e) {
 // Получение данных из формы
 e.preventDefault();
 let url = this.action;
 let params = new URLSearchParams(new FormData(this)).toString();
 ajaxSend(url, params, html, target);
});

let html = '\
<div class="Comments">\
<input type="hidden" name="slug" value="{{ slug }}">\
{{#comments}}\
<div class="Comment">\
    <div class="Comment-column Comment-column_pict">\
      <div class="Comment-avatar" style="background-image: url({{media}}{{{ user__avatar }}}); background-size: cover;"></div> \
    </div>\
    <div class="Comment-column">\
      <header class="Comment-header">\
        <div>\
          <strong class="Comment-title">{{ author }}\
          </strong><span class="Comment-date">{{ added }}</span>\
        </div>\
      </header>\
      <div class="Comment-content">{{ content }}</div>\
    </div>\
</div>\
{{/comments}}\
</div>\
{{#empty_pages}}\
<button type="Submit" id="btn_page" class="btn btn_default btn_sm">\
<select id="id_page" name="page" multiple>\
{{#has_previous}}\
<option class="btn btn_default btn_sm" value="1">1</option>\
<option class="btn btn_default btn_sm" value="{{ previous_page_number }}">&laquo;</option>\
{{/has_previous}}\
<option class="btn btn_default btn_sm active" value="{{ number }}">{{ number }}</option>\
{{#has_next }}\
<option class="btn btn_default btn_sm" value="{{next_page_number }}"> &raquo;</option>\
<option class="btn btn_default btn_sm" value="{{ num_pages }}"> &raquo;&raquo;</option>\
{{/has_next }}\
</select>\
</button>\
{{/empty_pages}}'
