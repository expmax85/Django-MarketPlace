window.addEventListener('DOMContentLoaded', (event) => {
	btns = document.getElementsByClassName('import__header');
	Array.from(btns).forEach(element => {

		element.addEventListener('click', function (event) {
			element.parentNode.classList.toggle('auto_height')
		})
	});

});