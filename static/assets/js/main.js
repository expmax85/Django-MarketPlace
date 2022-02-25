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