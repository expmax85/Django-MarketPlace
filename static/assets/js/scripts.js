'use strict';
(function ($) {

    var px = ''; //'rt--'

    /**
     * Функция для вывода набора jQuery по селектору, к селектору добавляются
     * префиксы
     *
     * @param {string} selector Принимает селектор для формирования набора
     * @return {jQuery} Возвращает новый jQuery набор по выбранным селекторам
     */
    function $x(selector) {
        return $(x(selector));
    }

    /**
     * Функция для автоматического добавления префиксов к селекторы
     *
     * @param {string} selector Принимает селектор для формирования набора
     * @return {string} Возвращает новый jQuery набор по выбранным селекторам
     */
    function x(selector) {
        var arraySelectors = selector.split('.'),
            firstNotClass = !!arraySelectors[0];

        selector = '';

        for (var i = 0; i < arraySelectors.length; i++) {
            if (!i) {
                if (firstNotClass) selector += arraySelectors[i];
                continue;
            }
            selector += '.' + px + arraySelectors[i];
        }

        return selector;
    }

// Прелоадер
    $(function () {

        var menu = function () {
            var $menuMain = $('.menu_main');
            $menuMain.css('position', 'absolute');
            var menuHeight = $('.menu_main').outerHeight();
            $menuMain.css('position', 'static');
            var $body = $('body');

            function refresh() {
                if (window.innerWidth < 991) {
                    // $('.menuModal').each(function(){
                    //     var $this = $(this);
                    //     setTimeout(function(){
                    //         if ($this.attr('height') > 0) {
                    //             $this.css('height', 0);
                    //         }
                    //     }, 100);
                    // });
                    $('.menuModal').css('height', 0);
                    $menuMain.css('position', 'absolute');
                    menuHeight = $('.menu_main').outerHeight();
                    $menuMain.css('position', 'static');
                } else {
                    menuHeight = $('.menu_main').outerHeight();
                    $('.menuModal')
                        .removeClass("menuModal_OPEN")
                        .css('height', '');
                    $body.removeClass("Site_menuOPEN");
                    $('.menuTrigger').removeClass("menuTrigger_OPEN");
                }
            }

            return {
                init: function () {
                    if (window.innerWidth < 991) {
                        $(".menuModal").css('height', menuHeight);
                        // Меню для мобильных
                        $(".menuTrigger").each(function () {
                            $($(this).attr('href')).css('height', 0);
                        });
                    }

                    $(".menuTrigger").click(function (e) {
                        var $this = $(this),
                            href = $this.attr("href");

                        if ($this.hasClass("menuTrigger_OPEN")) {
                            $body.removeClass("Site_menuOPEN");
                            $(href)
                                .removeClass("menuModal_OPEN")
                                .css('height', 0);
                            $this.removeClass("menuTrigger_OPEN");
                        } else {
                            $body.addClass("Site_menuOPEN");
                            $(href)
                                .addClass("menuModal_OPEN")
                                .css('height', menuHeight);
                            $this.addClass("menuTrigger_OPEN");
                        }
                        e.preventDefault();
                    });
                    $(window).on('resize', refresh);
                }
            };
        };
        menu().init();
        var search = function () {
            var $searchLink = $('.Header-searchLink');
            return {
                init: function () {
                    $searchLink.each(function () {
                        var $this = $(this);
                        $this.on('click', function () {
                            var $thisClick = $(this);
                            $thisClick.next('.Header-search').toggleClass('Header-search_open');
                        });
                    });
                }
            };
        };
        search().init();
        var form = function () {
            var $selectList = $('.selectList');
            var $input = $('.form-input, .form-textarea');
            var $form = $('.form');
            var $select = $('.form-select');
            return {
                init: function () {
                    $selectList.each(function () {
                        var $this = $(this),
                            $radio = $this.find('input[type="radio"]');

                        function changeTitle($block, $element) {
                            $block.find('.selectList-title')
                                .text($element.closest('.selectList-item')
                                    .find('.selectList-text').text())
                        }

                        changeTitle($this, $radio.filter('[checked="checked"]'));
                        $radio.on('change', function () {
                            changeTitle($this, $(this));
                        });

                    });
                    $(document).on('click', function (e) {
                        var $this = $(e.target);
                        if (!$this.hasClass('selectList-header')) {
                            $this = $(e.target).closest('.selectList-header');
                        }
                        if ($this.length) {
                            e.preventDefault();
                            $this.closest('.selectList').toggleClass('selectList_OPEN');
                        } else {
                            $('.selectList').removeClass('selectList_OPEN');
                        }
                    });

                    // Валидация полей
                    $input.on('blur', function () {
                        var $this = $(this),
                            validate = $this.data('validate'),
                            message = '',
                            error = false;
                        validate = validate.split(' ');
                        validate.forEach(function (v) {
                            switch (v) {
                                case 'require':
                                    if (!$this.val()) {
                                        message = 'Это поле обязательно для заполнения. ';
                                        error = true;
                                    }
                                    break;
                                case 'pay':
                                    var val = $this.val().replace(' ', '');
                                    val = val + '';
                                    if (parseFloat(val) % 2 !== 0) {
                                        message += 'Номер должен быть четным. ';
                                        error = true;
                                    }
                                    break;

                            }
                            if (error) {
                                if ($this.hasClass('form-input')) {
                                    $this.addClass('form-input_error');
                                }
                                if ($this.hasClass('form-textarea')) {
                                    $this.addClass('form-textarea_error');
                                }
                                if (!$this.next('.form-error').length) {
                                    $this.after('<div class="form-error">' + message + '</div>');
                                }
                                $this.data('errorinput', true);
                            } else {
                                $this.next('.form-error').remove();
                                $this.removeClass('form-input_error');
                                $this.removeClass('form-textarea_error');
                                $this.data('errorinput', false);
                            }
                            message = '';

                        });
                    });
                    $form.on('submit', function (e) {
                        var $this = $(this),
                            $validate = $this.find('[data-validate]');

                        $validate.each(function () {
                            var $this = $(this);
                            $this.trigger('blur');
                            if ($this.data('errorinput')) {
                                e.preventDefault();
                            }
                        });
                    });
                    $select.wrap('<div class="form-selectWrap"></div>');
                    $('[data-mask]').each(function () {
                        var $this = $(this);
                        $this.mask($this.data('mask'), {placeholder: 'x'});
                    });
                }
            };
        };
        form().init();
        let modal = function () {
            let $trigger = $('.trigger'),
                $body = $('body'),
                $modal = $('.modal');

            let template = {
                img: (img) => '<div class="modal">' +
                    '<div class="modal-window">' +
                    '<a href="#" class="modal-close fa fa-close"></a>' +
                    '<img src="' + img + '" />' +
                    '</div>' +
                    '</div>'
            };

            return {
                refresh: function () {
                },
                init: function () {
                    function modalClick(e) {

                        let $target = $(e.target),
                            $this = $(this);

                        if ($target.hasClass('modal-close')) {
                            $target = $this;
                        }

                        if ($this.is($target)) {
                            e.preventDefault();
                            $body.removeClass("Site_modalOPEN");
                            $this.removeClass("modal_OPEN");
                            $('[href="' + $this.attr('id') + '"]').removeClass("trigger_OPEN");
                        }
                    }

                    $trigger.click(function (e) {
                        e.preventDefault();

                        let $this = $(this),
                            href = $this.attr("href"),
                            $href = $(href);

                        if (!$(href).length) {
                            let $img = $(template.img($this.data('src')));
                            $img.attr('id', href.replace('#', ''));
                            $body.append($img);
                            $href = $(href);
                            $modal = $modal.add($href);
                            $href.click(modalClick);
                        }

                        $href.addClass("modal_OPEN");
                        $body.addClass("Site_modalOPEN");
                        $this.addClass("trigger_OPEN");
                    });

                    $modal.click(modalClick);

                }
            };
        };

        modal().init();
        var range = function () {
            return {
                init: function () {
                    var $range = $('.range'),
                        $line = $range.find('.range-line');

                    $line.ionRangeSlider({
                        onStart: function (data) {
                            $('.rangePrice').text(
                                '$' + data.from + ' - $' + data.to
                            )
                        },
                        onChange: function (data) {
                            $('.rangePrice').text(
                                '$' + data.from + ' - $' + data.to
                            )
                        }
                    });
                }
            };
        };
        range().init();
        var table = function () {
            return {
                init: function () {
                }
            };
        };
        table().init();
//END
        var PanelAdd = function () {
            return {
                init: function () {
                }
            };
        };
        PanelAdd().init();
        var ControlPanel = function () {
            return {
                init: function () {
                }
            };
        };
        ControlPanel().init();
        var Slider = function () {
            let $block = $('.Slider').not('.Slider_carousel'),
                $container = $block.children('.Slider-box'),
                $carousel = $('.Slider_carousel'),
                $containerCar = $carousel.children('.Slider-box');
            return {
                init: function () {
                    $container.each(function () {
                        var $this = $(this);
                        var $navigate = $this.closest($block).find('.Slider-navigate');
                        $this.slick({
                            dots: true,
                            arrows: true,
                            autoplay: true,
                            appendArrows: $navigate,
                            appendDots: $navigate,
                            autoplaySpeed: 3000
                        });
                    });
                    $containerCar.each(function () {
                        var $this = $(this);
                        var $navigate = $this.closest($carousel).find('.Slider-navigate');
                        if ($this.hasClass('Cards_hz')) {
                            $this.slick({
                                appendArrows: $navigate,
                                appendDots: $navigate,
                                dots: true,
                                arrows: true,
                                slidesToShow: 3,
                                slidesToScroll: 2,
                                responsive: [
                                    {
                                        breakpoint: 1600,
                                        settings: {
                                            slidesToShow: 2,
                                            slidesToScroll: 2
                                        }
                                    },
                                    {
                                        breakpoint: 900,
                                        settings: {
                                            slidesToShow: 1,
                                            slidesToScroll: 1
                                        }
                                    }
                                ]
                            });

                        } else {
                            $this.slick({
                                appendArrows: $navigate,
                                appendDots: $navigate,
                                dots: true,
                                arrows: true,
                                slidesToShow: 4,
                                slidesToScroll: 2,
                                responsive: [
                                    {
                                        breakpoint: 1600,
                                        settings: {
                                            slidesToShow: 3,
                                            slidesToScroll: 2
                                        }
                                    },
                                    {
                                        breakpoint: 1230,
                                        settings: {
                                            slidesToShow: 2,
                                            slidesToScroll: 2
                                        }
                                    },
                                    {
                                        breakpoint: 570,
                                        settings: {
                                            slidesToShow: 1,
                                            slidesToScroll: 1
                                        }
                                    }
                                ]
                            });

                        }
                    });

                }
            };
        };
        Slider().init();
        var CartBlock = function () {
            return {
                init: function () {
                }
            };
        };
        CartBlock().init();
        var CategoriesButton = function () {
            return {
                init: function () {
                    $(document).on('click', function (e) {
                        var $this = $(e.target);
                        if ($this.is('a.CategoriesButton-arrow') && $this.closest('.CategoriesButton-link').length) {
                            e.preventDefault();
                            if ($this.next('.CategoriesButton-submenu').is(':visible')) {
                                $('.CategoriesButton .CategoriesButton-submenu').hide(0);
                            } else {
                                $('.CategoriesButton .CategoriesButton-submenu').hide(0);
                                $this.next('.CategoriesButton-submenu').show(0);
                            }
                        } else {
                            if (!$this.hasClass('CategoriesButton-title')) {
                                $this = $(e.target).closest('.CategoriesButton-title');
                            }
                            if ($this.length) {
                                e.preventDefault();
                                $this.closest('.CategoriesButton').toggleClass('CategoriesButton_OPEN');
                            } else {
                                $('.CategoriesButton').removeClass('CategoriesButton_OPEN');
                                $('.CategoriesButton .CategoriesButton-submenu').hide(0);
                            }
                        }
                    });
                }
            };
        };
        CategoriesButton().init();
        var Middle = function () {
            return {
                init: function () {
                }
            };
        };
        Middle().init();
        var Section = function () {
            return {
                init: function () {
                }
            };
        };
        Section().init();
        var BannersHome = function () {
            return {
                init: function () {
                }
            };
        };
        BannersHome().init();
        var Card = function () {
            return {
                init: function () {
                }
            };
        };
        Card().init();
        var CountDown = function () {
            var $blocks = $('.CountDown');

            function getTimeRemaining(endtime) {
                endtime = endtime.split(' ');
                var date = endtime[0].split('.');
                var time = endtime[1].split(':');
                var t = new Date(date[2], date[1] - 1, date[0] - 1, time[0], time[1]) - new Date();
                var seconds = Math.floor((t / 1000) % 60);
                var minutes = Math.floor((t / 1000 / 60) % 60);
                var hours = Math.floor((t / (1000 * 60 * 60)) % 24);
                var days = Math.floor(t / (1000 * 60 * 60 * 24));
                return {
                    'total': t,
                    'days': days,
                    'hours': hours,
                    'minutes': minutes,
                    'seconds': seconds
                };
            }

            function initializeClock(clock, endtime) {
                function updateClock() {
                    var t = getTimeRemaining(endtime);
                    clock.find('.CountDown-days').text(t.days);
                    clock.find('.CountDown-hours').text(t.hours);
                    clock.find('.CountDown-minutes').text(t.minutes);
                    clock.find('.CountDown-secs').text(t.seconds);
                    if (t.total <= 0) {
                        clearInterval(timeinterval);
                    }
                }

                updateClock();
                var timeinterval = setInterval(updateClock, 1000);
            }

            return {
                init: function () {
                    $blocks.each(function () {
                        var $this = $(this);
                        initializeClock($this, $this.data('date'));
                    });
                }
            };
        };
        CountDown().init();
        var Rating = function () {
            return {
                init: function () {
                    $('.Rating_input:not(.Rating_inputClick)').on('click', function () {
                        $(this).addClass('Rating_inputClick');
                    });
                }
            };
        };
        Rating().init();
        var Choice = function () {
            return {
                init: function () {
                }
            };
        };
        Choice().init();
        var Map = function () {
            return {
                init: function () {
                }
            };
        };
        Map().init();
        var Pagination = function () {
            return {
                init: function () {
                }
            };
        };
        Pagination().init();
        var Sort = function () {
            return {
                init: function () {
                }
            };
        };
        Sort().init();
        var Compare = function () {
            var $compare = $('.Compare');
            var $products = $compare.find('.Compare-products');
            var $checkDifferent = $('.Compare-checkDifferent input');
            return {
                init: function () {
                    $products.on('scroll', function () {
                        var $this = $(this);
                        $products.each(function () {
                            $(this)[0].scrollLeft = $this[0].scrollLeft;
                        })
                    });
                    $checkDifferent.on('change', function () {
                        var $this = $(this),
                            $rowsHide = $this.closest($compare).find('.Compare-row_hide');
                        if ($this.prop('checked')) {
                            $rowsHide.hide(0);
                        } else {
                            $rowsHide.show(0);
                        }
                    });
                    $checkDifferent.trigger('change');
                }
            };
        };
        Compare().init();
        var Sort = function () {
            return {
                init: function () {
                }
            };
        };
        Sort().init();
        var NavigateProfile = function () {
            return {
                init: function () {
                }
            };
        };
        NavigateProfile().init();
        var Profile = function () {
            var $avatar = $('.Profile-avatar');
            return {
                init: function () {
                    var $avatarfile = $avatar.find('.Profile-file');

                    function readURL(input) {
                        if (input.files && input.files[0]) {
                            var file = input.files[0],
                                ext = 'неизвестно';
                            ext = file.name.split('.').pop();
                            if (ext === 'png' || ext === 'jpg' || ext === 'gif') {
                                var reader = new FileReader();

                                reader.onload = function (e) {
                                    $(input).closest($avatar).find('.Profile-img img').attr('src', e.target.result);
                                }

                                reader.readAsDataURL(file);
                                return true;
                            }
                            return false;
                        }
                    }

                    $avatarfile.change(function () {
                        var $thisAvatar = $(this).closest($avatar);
                        if (readURL(this)) {
                            $thisAvatar.removeClass('Profile-avatar_noimg');
                            $thisAvatar.next('.form-error').remove();
                            $thisAvatar.find('input[type="file"]').data('errorinput', false);
                        } else {
                            if (!$thisAvatar.next('.form-error').length) {
                                $thisAvatar.find('input[type="file"]').data('errorinput', true);
                                $thisAvatar.after('<div class="form-error">Для загрузки допустимы лишь картинки с расширением png, jpg, gif</div>');
                            }
                        }
                        ;
                    });
                }
            };
        };
        Profile().init();
        var Cart = function () {
            return {
                init: function () {
                }
            };
        };
        Cart().init();
        var Amount = function () {
            var $amount = $('.Amount');
            var $add = $('.Amount-add');
            var $input = $('.Amount-input');
            var $remove = $('.Amount-remove');
            return {
                init: function () {
                    $add.on('click', function (e) {
                        e.preventDefault();
                        var $inputThis = $(this).siblings($input).filter($input);
                        var value = parseFloat($inputThis.val());
                        $inputThis.val(value + 1);
                    });
                    $remove.on('click', function (e) {
                        e.preventDefault();
                        var $inputThis = $(this).siblings($input).filter($input);
                        var value = parseFloat($inputThis.val());
                        $inputThis.val(value > 0 ? value - 1 : 0);
                    });
                }
            };
        };
        Amount().init();
        var Order = function () {
            var $next = $('.Order-next'),
                $blocks = $('.Order-block'),
                $navigate = $('.Order-navigate');
            return {
                init: function () {
                    $next.add($navigate.find('.menu-link')).on('click', function (e) {
                        e.preventDefault();
                        var $this = $(this),
                            href = $this.attr('href'),
                            error = false,
                            $validate = $this.closest($blocks).find('[data-validate]')
                        if ($(e.target).is('.Order-next')) {
                            $validate.each(function () {
                                var $this = $(this);
                                $this.trigger('blur');
                                if ($this.data('errorinput')) {
                                    error = true
                                }
                            });
                        }
                        if (error === false && ($(e.target).is('.Order-next') ||
                            $blocks.index($(href)) < $blocks.index($blocks.filter('.Order-block_OPEN')))
                        ) {
                            $blocks.removeClass('Order-block_OPEN');
                            $(href).addClass('Order-block_OPEN');
                            $navigate.find('.menu-item').removeClass('menu-item_ACTIVE');
                            $navigate.find('.menu-link[href="' + href + '"]')
                                .closest('.menu-item')
                                .addClass('menu-item_ACTIVE');
                        }

                    });
                }
            };
        };
        Order().init();
        var Account = function () {
            return {
                init: function () {
                }
            };
        };
        Account().init();
        var Payment = function () {
            return {
                init: function () {
                    $('.Payment-generate').on('click', function (e) {
                        var $this = $(this),
                            $bill = $this.closest('.Payment').find('.Payment-bill'),
                            billNumber = '';
                        e.preventDefault();
                        do {
                            billNumber = Math.random() + '';
                            billNumber = billNumber.slice(-9, -1);
                        } while (parseFloat(billNumber) % 2 !== 0);
                        billNumber = billNumber.slice(0, 4) + ' ' + billNumber.slice(4, 8);
                        $bill.val(billNumber);
                    });
                    $('.Payment-pay .btn').on('click', function (e) {
                        var $this = $(this),
                            $validate = $this.closest('.form').find('[data-validate]');

                        $validate.each(function () {
                            var $this = $(this);
                            $this.trigger('blur');
                            if ($this.data('errorinput')) {
                                e.preventDefault();
                            }
                        });
                    });
                }
            };
        };
        Payment().init();
        var Tabs = function () {
            var $tabs = $('.Tabs');
            var $tabsLink = $('.Tabs-link');
            var $tabsBlock = $('.Tabs-block');
            return {
                init: function () {
                    // var $steps = $('.Tabs_steps');
                    // var $step = $steps.find($tabsLink).not($steps.find($tabs).find($tabsLink));
                    // var $blocks = $steps.find($tabsBlock).not($steps.find($tabs).find($tabsBlock));
                    // $blocks.hide(0);
                    // var href = $step.eq(0).attr('href');
                    // var $active = $(href);
                    // var $links= $step.add($step.siblings($tabsLink));
                    // $links.removeClass('Tabs-link_ACTIVE');
                    // $step.eq(0).addClass('Tabs-link_ACTIVE');
                    // $active.show(0);

                    $tabsLink.on('click', function (e) {
                        var $this = $(this);
                        var href = $this.attr('href');
                        if (href[0] === "#") {
                            e.preventDefault();
                            var $parent = $this.closest($tabs);
                            if ($parent.hasClass('Tabs_steps')) {
                            } else {
                                var $blocks = $parent.find($tabsBlock).not($parent.find($tabs).find($tabsBlock));
                                var $links = $this.add($this.siblings($tabsLink));
                                var $active = $(href);
                                $links.removeClass('Tabs-link_ACTIVE');
                                $this.addClass('Tabs-link_ACTIVE');
                                $blocks.hide(0);
                                $active.show(0);
                            }
                        }

                    });
                    $('.TabsLink').on('click', function (e) {
                        var $this = $(this);
                        var href = $this.attr('href');
                        var $active = $(href);
                        var $parent = $active.closest($tabs);
                        if ($parent.hasClass('Tabs_steps')) {
                        } else {
                            var $blocks = $parent.find($tabsBlock).not($parent.find($tabs).find($tabsBlock));
                            var $link = $('.Tabs-link[href="' + href + '"]');
                            var $links = $link.add($link.siblings($tabsLink));
                            $links.removeClass('Tabs-link_ACTIVE');
                            $link.addClass('Tabs-link_ACTIVE');
                            $blocks.hide(0);
                            $active.show(0);
                        }

                    });
                    $tabs.each(function () {
                        $(this).find($tabsLink).eq(0).trigger('click');
                    });
                }
            };
        };
        Tabs().init();
// setTimeout(function(){
//     $('body').css('opacity', '1');
// }, 100);
        var ProductCard = function () {
            var $picts = $('.ProductCard-pict');
            var $photo = $('.ProductCard-photo');
            return {
                init: function () {
                    $picts.on('click', function (e) {
                        e.preventDefault();
                        var $this = $(this);
                        var href = $this.attr('href');
                        $photo.empty();
                        $photo.append('<img src="' + href + '" />');
                        $picts.removeClass('ProductCard-pict_ACTIVE');
                        $this.addClass('ProductCard-pict_ACTIVE');
                    });
                }
            };
        };
        ProductCard().init();
        var Comments = function () {
            return {
                init: function () {
                    $('[data-action="comments-show"]').on('click', function (e) {
                        e.preventDefault();
                        var $this = $(this),
                            text = $this.data('text-alt'),
                            $comments = $this.prev('.Comments').find('.Comments-wrap_toggle');
                        $this.data('text-alt', $this.text());
                        $this.text(text);
                        $comments
                            .toggleClass('Comments-wrap_HIDE');
                        $('.fixScrollBlock').trigger('render.airStickyBlock');
                    });
                }
            };
        };
        Comments().init();
        var Product = function () {
            return {
                init: function () {
                }
            };
        };
        Product().init();
        var ProgressPayment = function () {
            return {
                init: function () {
                }
            };
        };
        ProgressPayment().init();
        var Categories = function () {
            return {
                init: function () {
                    if ($(window).width() < 990) {
                        var $more = $('.Categories-more'),
                            $trigger = $('.Categories-trigger');
                        $trigger.on('click', function (e) {
                            e.preventDefault();
                            var $this = $(this),
                                text = $this.data('text-alt'),
                                $block = $this.prev($more);
                            $this.data('text-alt', $this.text());
                            $this.text(text);
                            $this.toggleClass('Categories-trigger_OPEN');
                            $block.toggle(0);
                        });
                    }
                }
            };
        };
        Categories().init();
//ENDion.js
//END


    });


})(jQuery);


// ============================= try async to sort items in catalog =======================================

function adjustSortBtn(data, sortType) {
    document.querySelectorAll('.Sort-sortBy').forEach(btn => {
            document.querySelector('.Sort-title').dataset.sort_title = sortType
            if (btn.dataset.sort === data.current_state) {
                if (btn.classList.contains('Sort-sortBy_dec') && !btn.classList.contains('Sort-sortBy_inc')) {
                    btn.classList.remove('Sort-sortBy_dec')
                    btn.classList.add('Sort-sortBy_inc')
                    btn.dataset.sort = data.next_state
                    return
                }
                if (btn.classList.contains('Sort-sortBy_inc') && !btn.classList.contains('Sort-sortBy_dec')) {
                    btn.classList.remove('Sort-sortBy_inc')
                    btn.classList.add('Sort-sortBy_dec')
                    btn.dataset.sort = data.next_state
                    return
                }
                if (!btn.classList.contains('Sort-sortBy_inc') && !btn.classList.contains('Sort-sortBy_dec')) {
                    btn.classList.add('Sort-sortBy_inc')
                    btn.dataset.sort = data.next_state
                }

            } else {
                btn.classList.remove('Sort-sortBy_dec')
                btn.classList.remove('Sort-sortBy_inc')
                btn.dataset.sort = btn.dataset.name + '_inc'
            }

            document.getElementById('pagination_settings').dataset.sort = data.current_state
            document.getElementById('submit_btn').dataset.sort = data.current_state
        }
    );
}

function createURL(url) {

    const filter_status = document.getElementById('submit_btn').dataset.active;
    const tag_status = document.getElementById('tag_status').dataset.tag_active;
    const tag_name = document.getElementById('tag_status').dataset.tag_name;

    const form = document.forms.filterForm;

    if (filter_status == 1 && tag_status == 0) {

        let price = form.elements.price.value;
        let title = form.elements.title.value;
        let select = form.elements.select.value;
        if (select == "select") {
            select = '';
        }
        let in_stock = form.elements.in_stock.value;
        let is_hot = form.elements.is_hot.value;
        url = url + `price=${price}&title=${title}&select=${select}&in_stock=${in_stock}&is_hot=${is_hot}`
    }
    if (filter_status == 1 && tag_status == 1) {

        let price = form.elements.price.value;
        let title = form.elements.title.value;
        let select = form.elements.select.value;
        if (select == "select") {
            select = '';
        }
        let in_stock = form.elements.in_stock.value;
        let is_hot = form.elements.is_hot.value;
        url = url + `price=${price}&title=${title}&select=${select}&in_stock=${in_stock}&is_hot=${is_hot}&tag=${tag_name}`
    }
    if (filter_status == 0 && tag_status == 1) {
        url = url + `tag=${tag_name}`
    }
    if (filter_status == 0 && tag_status == 0) {
        url = url + '';
    }

    return url
}

function sortFoo() {
    document.querySelectorAll('.Sort-sortBy').forEach(function (sortBtn) {
        sortBtn.addEventListener('click', async (event) => {

            const sortType = event.currentTarget.dataset.sort;
            let url_base = `/async_catalog?sort_type=${sortType}&`

            let preUrl = getURL(url_base)
            let url = createURL(preUrl)
            console.log(url)

            const response = await fetch(url);
            const data = await response.json();
            $('#cards_with_pagination').replaceWith($(data.html));

            adjustSortBtn(data, sortType)
            paginationFoo()
        })
    });
}

// ============================= async pagination in catalog =======================================
function getURL(url_base) {
    const paramsString = document.location.search;
    const searchParams = new URLSearchParams(paramsString);

    if (searchParams.has("slug")) {
        url_base = url_base + `slug=${searchParams.get("slug")}&`
    }
    if (searchParams.has("query")) {
        url_base = url_base + `query=${searchParams.get("query")}&`
    }
    if (searchParams.has("main_tag")) {
        url_base = url_base + `main_tag=${searchParams.get("main_tag")}&`
    }
    if (!searchParams.has("slug") && !searchParams.has("query") && !searchParams.has("main_tag")) {
        url_base = url_base + ''
    }
    return url_base
}

async function paginationCardRender(url, page) {
    const responsePages = await fetch(url);
    const data = await responsePages.json();
    $('#cards_with_pagination').replaceWith($(data.html))

    document.getElementById('prevPage').dataset.page = data.prev_page;
    document.getElementById('nextPage').dataset.page = data.next_page;
    document.querySelectorAll('.Pagination-element').forEach(btn => {
        if (btn.dataset.name === page) {
            btn.classList.add('Pagination-element_current')
        } else {
            btn.classList.remove('Pagination-element_current')
        }
    })
}

function paginationFoo() {
    document.querySelectorAll('.Pagination-element').forEach(function (pageBtn) {
        pageBtn.addEventListener('click', async (event) => {

            const page = event.currentTarget.dataset.page;
            const sort = document.getElementById('pagination_settings').dataset.sort;
            let url_base = `/async_catalog?page=${page}&sort_type=${sort}&`

            let url = getURL(url_base)
            console.log(url)
            await paginationCardRender(url, page)
            paginationFoo()

        })
    });
}

// ============================= queryset with filters =======================================

async function filterCardRender(url) {
    const response = await fetch(url);
    const data = await response.json();

    $('#cards_with_pagination').replaceWith($(data.html));
}

function filterFoo() {
    document.getElementById('submit_btn').addEventListener('click', async (filterBtn) => {

        let filterDataset = document.getElementById('submit_btn').dataset
        filterDataset.active = 1;

        const sortType = filterDataset.sort;
        let url_base = `/async_catalog?sort_type=${sortType}&`
        let preUrl = getURL(url_base)

        let url = createURL(preUrl)
        console.log(url)
        await filterCardRender(url)

        paginationFoo()
    });

}

// ============================================ queryset with tag ========================================

async function tagCardRender(url) {
    const response = await fetch(url);
    const data = await response.json();
    $('#cards_with_pagination').replaceWith($(data.html));
}

function adjustSettingsTagBtn(someClickedBtn, btnDataset, oldStyle) {
    if (btnDataset.in_use === '0') {
        btnDataset.in_use = 1
        document.getElementById('tag_status').dataset.tag_name = btnDataset.tag
        document.getElementById('tag_status').dataset.tag_active = 1

        document.querySelectorAll('.tag_btn').forEach(function (elem) {
            if (elem !== someClickedBtn) {
                elem.style = oldStyle
                elem.dataset.in_use = '0'
            } else {
                elem.classList.add('active_tag')
                elem.style.borderColor = '#0063d1';
            }
        })

    } else {
        btnDataset.in_use = '0'
        document.getElementById('tag_status').dataset.tag_name = ''
        document.getElementById('tag_status').dataset.tag_active = 0
        document.querySelectorAll('.tag_btn').forEach(function (elem) {
            elem.style = oldStyle
            elem.dataset.in_use = '0'
            elem.classList.remove('active_tag')
        })

    }
}

function getOldStyle() {
    const allTagBtn = document.querySelectorAll('.tag_btn')
    for (let tagBtn of allTagBtn) {
        if (tagBtn.dataset.in_use === 0) {
            const oldStyle = tagBtn.style
            return oldStyle
        }
    }
}

function tagFoo() {
    document.querySelectorAll('.tag_btn').forEach(function (tagBtn) {
        tagBtn.addEventListener('click', async (event) => {

            const currentBtn = event.currentTarget
            const tagDataset = currentBtn.dataset;
            const oldStyle = getOldStyle()

            adjustSettingsTagBtn(currentBtn, tagDataset, oldStyle)

            const sortType = document.querySelector('.Sort-title').dataset.sort_title;

            let url_base = `/async_catalog?sort_type=${sortType}&`
            let preUrl = getURL(url_base)
            let url = createURL(preUrl)

            console.log(url)

            await tagCardRender(url)

            paginationFoo()
        })
    });
}

// ============================================= check boxes in filter changes ========================================

function checkBoxFoo() {
    document.querySelectorAll('.che').forEach(function (box) {
        box.addEventListener('click', function (event) {
            const checkbox = event.currentTarget
            if (checkbox.checked) {
                checkbox.value = '1';
            } else {
                checkbox.value = '0';
            }
        })
    });
}

// ======================================= search by input ===========================================================

function searchFoo(some_page) {
    document.getElementById('search_btn').addEventListener('click', function () {

        const form = document.forms.search_form;
        let full_url = `/catalogs/`

        if (some_page === undefined) {
            const search_query = form.elements.query.value;
            full_url = full_url + `?query=${search_query}`
        }
        if (some_page !== undefined) {
            const search_query = form.elements.query.value;
            full_url = full_url + `?query=${search_query}&page=${some_page}`
        }

        console.log(full_url)
        window.location.href = full_url

        paginationFoo()
    })
}

// ======================================  set languages ==============================================================

function getCookie(name) {
    var value = '; ' + document.cookie,
        parts = value.split('; ' + name + '=');
    if (parts.length == 2) return parts.pop().split(';').shift();
}

function reload_page() {
    window.location.reload(true);
}

async function setLanguage() {
    document.querySelectorAll('.lang_btn').forEach(function (langBtn) {

        langBtn.addEventListener('click', async (event) => {

            let target = event.currentTarget

            if (!target.classList.contains('selected_lang')) {
                let url = target.dataset.href
                const language_code = target.dataset.language_code

                let data = new FormData();
                data.append('LANGUAGE_QUERY_PARAMETER', language_code);

                console.log(url)

                const trueRequest = new XMLHttpRequest();
                trueRequest.open('POST', url, true);
                trueRequest.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                trueRequest.send(data);
                trueRequest.onload = function () {
                    reload_page();
                }
            }

        })
    })
}

// ===================================  main function which starts all needed for catalog ==============================

function main() {
    document.addEventListener('DOMContentLoaded', function () {
        if (document.querySelectorAll('.che').length > 0) {
            checkBoxFoo()
        }

        if (document.querySelectorAll('.Sort-sortBy').length > 0) {
            sortFoo()
        }

        if (document.querySelectorAll('.Pagination-element').length > 0) {
            paginationFoo()
        }

        if (document.querySelectorAll('.tag_btn').length > 0) {
            tagFoo()
        }

        if (document.getElementById('search_div')) {
            searchFoo()
        }

        if (document.querySelectorAll('#submit_btn').length > 0) {
            filterFoo()
            document.querySelectorAll('.CategoriesButton-link').forEach(function (categoryBtn) {
                document.getElementById('submit_btn').dataset.active = 0
            });
        }
        setLanguage()
    });
}

main()
