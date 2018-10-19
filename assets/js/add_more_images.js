len = document.querySelectorAll('.table').length;


$('#add_more').click(function() {
    if ( len < 5 )
    {
      cloneMore('div.table:last', 'service');
      len++;
    }
    if (len >= 5 )
      $('#add_more').remove();

});
