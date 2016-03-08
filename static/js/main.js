function format ( d ) {
    var responseHTML = ''
   $.ajax({
      url: '/details?opp_id=' + d.Id,
      async: false,
      success: function(data) {
        responseHTML += data
      }
    });
    console.log(responseHTML); 
    return responseHTML
}
$(document).ready(function() {
    $('#opps tbody').on('click', '#search', function(ev){
      alert('hi');
      var responseHTML = ''
      var q = $('#search-box').val();
      var id = this.data('opp-id');
      $.ajax({
        url: '/details?opp_id=' + id +'&q='+ q,
        async: false,
        success: function(data) {
          responseHTML += data
          console.log(responseHTML);   
        }
      });
    });
    var table = $('#opps').DataTable({
      columns: [
        { 'data': 'StageName'},
        { 'data': 'Name'},
        { 'data': 'Event_Date__c'},
        { 'data': 'Client_Total__c'},
        { 'data': 'Number_of_Pitched_Experiences__c'},
        { 'data': 'Contact_Name'},
      ],
      paging: false,
      ajax: {
        url: '/results'
      }
      });
    table.ajax.url('/results').load()
    // Add event listener for opening and closing details
    $('#opps tbody').on('click', '[role="row"]', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
 
        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
        }
    } );
} );
