
(function($){

    $.fn.notify = function(text, clazz) {
        var $div = $('<div style="width:100%;position:fixed;bottom:2em;z-index:1051;text-align:center;">');
        var $span = $('<span class="alert">').addClass(clazz).html(text);
        $div.append($span);
        $(this).css('position','relative').append($div);
        setTimeout(function(){ $div.remove(); }, 5000);
    };

    $.fn.asyncSubmit = function(evt) {
        if(!evt) evt = window.event;
        if(evt && ('preventDefault' in evt)) {
            evt.preventDefault();
        }


        var $this = $(this);
        var action = $(this).attr('action');
        var method = $(this).attr('method');
        
        var data = {};
        $(this).find(':input').each(function(i,e){
            data[ $(e).attr('name') ] = $(e).val();
        });

        request = $.ajax({
          url: action,
          type: method,
          data: data
        })
          .fail(function(){
            $this.addClass('.has-error');
            $(document.body).notify('Mensagem não enviada!', 'alert-danger');
        })
          .done(function(){
            $this.removeClass('.has-error');
            $("#modal-contact").modal("hide");
            $(document.body).notify('Mensagem enviada!', 'alert-success');
        });
    };
})(jQuery);