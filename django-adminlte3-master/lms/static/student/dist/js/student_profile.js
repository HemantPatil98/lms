(function() {

    var db = {

        // loadData: function(filter) {
        //     return $.grep(this.clients, function(client) {
        //         return (!filter.Name || client.Name.indexOf(filter.Name) > -1)
        //             && (filter.Age === undefined || client.Age === filter.Age)
        //             && (!filter.Address || client.Address.indexOf(filter.Address) > -1)
        //             && (!filter.Country || client.Country === filter.Country)
        //             && (filter.Married === undefined || client.Married === filter.Married);
        //     });
        // },
        loadData: function(filter) {
                    // console.log(filter.name);
            return $.grep(this.data, function(client) {
                // console.log(!filter.name || client.name.indexOf(filter.name)>-1);
                return (!filter.id || client.id.indexOf(filter.id) > -1)
                && (!filter.name || client.name.indexOf(filter.name) > -1)
                && (!filter.contact || client.contact.indexOf(filter.contact) > -1)
                && (!filter.emailid || client.emailid.indexOf(filter.emailid) > -1)
                && (!filter.dateofadmission || client.dateofadmission.indexOf(filter.dateofadmission) > -1)
                && (!filter.trainingmode || client.trainingmode.indexOf(filter.trainingmode) > -1)
                && (!filter.batchstartdate || client.batchstartdate.indexOf(filter.batchstartdate) > -1)
                && (!filter.course || client.course.indexOf(filter.course) > -1)
                && (!filter.startcourse || client.startcourse.indexOf(filter.startcourse) > -1)
                && (!filter.currentmodule || client.currentmodule.indexOf(filter.currentmodule) > -1)
                && (!filter.ctrainername || client.ctrainername.indexOf(filter.ctrainername) > -1)
                && (!filter.cmodulestartdate || client.cmodulestartdate.indexOf(filter.cmodulestartdate) > -1)
                && (!filter.cmoduleenddate || client.cmoduleenddate.indexOf(filter.cmoduleenddate) > -1)
                && (!filter.ctheory || client.ctheory.indexOf(filter.ctheory) > -1)
                && (!filter.cpracticle || client.cpracticle.indexOf(filter.cpracticle) > -1)
                && (!filter.coral || client.coral.indexOf(filter.coral) > -1)
                && (!filter.ctotal || client.ctotal.indexOf(filter.ctotal) > -1)
                && (!filter.sqltrainername || client.sqltrainername.indexOf(filter.sqltrainername) > -1)
                && (!filter.sqlmodulestartdate || client.sqlmodulestartdate.indexOf(filter.sqlmodulestartdate) > -1)
                && (!filter.sqlmoduleenddate || client.sqlmoduleenddate.indexOf(filter.sqlmoduleenddate) > -1)
                && (!filter.sqltheory || client.sqltheory.indexOf(filter.sqltheory) > -1)
                && (!filter.sqlpracticle || client.sqlpracticle.indexOf(filter.sqlpracticle) > -1)
                && (!filter.sqloral || client.sqloral.indexOf(filter.sqloral) > -1)
                && (!filter.sqltotal || client.sqltotal.indexOf(filter.sqltotal) > -1)
                && (!filter.wdtrainername || client.wdtrainername.indexOf(filter.wdtrainername) > -1)
                && (!filter.wdmodulestartdate || client.wdmodulestartdate.indexOf(filter.wdmodulestartdate) > -1)
                && (!filter.wdmoduleenddate || client.wdmoduleenddate.indexOf(filter.wdmoduleenddate) > -1)
                // && (!filter.wdtheory || client.wdctheory.indexOf(filter.wdtheory) > -1)
                && (!filter.wdpracticle || client.wdpracticle.indexOf(filter.wdpracticle) > -1)
                && (!filter.wdoral || client.wdoral.indexOf(filter.wdoral) > -1)
                && (!filter.wdtotal || client.wdtotal.indexOf(filter.wdtotal) > -1)
                && (!filter.portfoliolink || client.portfoliolink.indexOf(filter.portfoliolink) > -1)
                && (!filter.mock1 || client.mock1.indexOf(filter.mock1) > -1)
                && (!filter.coretrainername || client.coretrainername.indexOf(filter.coretrainername) > -1)
                && (!filter.coremodulestartdate || client.coremodulestartdate.indexOf(filter.coremodulestartdate) > -1)
                && (!filter.coremoduleenddate || client.coremoduleenddate.indexOf(filter.coremoduleenddate) > -1)
                && (!filter.coretheory || client.coretheory.indexOf(filter.coretheory) > -1)
                && (!filter.corepracticle || client.corepracticle.indexOf(filter.corepracticle) > -1)
                && (!filter.coreoral || client.coreoral.indexOf(filter.coreoral) > -1)
                && (!filter.coretotal || client.coretotal.indexOf(filter.coretotal) > -1)
                && (!filter.mock2 || client.mock2.indexOf(filter.mock2) > -1)
                && (!filter.advtrainername || client.advtrainername.indexOf(filter.advtrainername) > -1)
                && (!filter.advmodulestartdate || client.advmodulestartdate.indexOf(filter.advmodulestartdate) > -1)
                && (!filter.advmoduleenddate || client.advmoduleenddate.indexOf(filter.advmoduleenddate) > -1)
                && (!filter.advtheory || client.advtheory.indexOf(filter.advtheory) > -1)
                && (!filter.advpracticle || client.advpracticle.indexOf(filter.advpracticle) > -1)
                && (!filter.advoral || client.advoral.indexOf(filter.advoral) > -1)
                && (!filter.advtotal || client.advtotal.indexOf(filter.advtotal) > -1)
                && (!filter.fullcourseenddate || client.fullcourseenddate.indexOf(filter.fullcourseenddate) > -1)
                && (!filter.cravitaprojectstartdate || client.cravitaprojectstartdate.indexOf(filter.cravitaprojectstartdate) > -1)
                && (!filter.mock3 || client.mock3.indexOf(filter.mock3) > -1)
                && (!filter.softskillmark || client.softskillmark.indexOf(filter.softskillmark) > -1)
                && (!filter.finalmock || client.finalmock.indexOf(filter.finalmock) > -1)
                && (!filter.totalmarks || client.totalmarks.indexOf(filter.totalmarks) > -1)
                && (!filter.eligibleforplcement || client.eligibleforplcement.indexOf(filter.eligibleforplcement) > -1)
                && (!filter.remark || client.remark.indexOf(filter.remark) > -1);

            });
        },

        // insertItem: function(insertingClient) {
        //     this.clients.push(insertingClient);
        // },

        updateItem: function(rowIndex,updatingRow) { 
            console.log(updatingRow);
            // alert(1);
            Url = 'window.location.origin/setdata/profile/?row='+rowIndex+'&rowv='+updatingRow;
            data={
                row:updatingRow,
            }
            // $('.btn').click(function(){
                $.get(Url,function(data,status){
                    console.log(data);
                });
            // });
        },

        // deleteItem: function(deletingClient) {
        //     var clientIndex = $.inArray(deletingClient, this.clients);
        //     this.clients.splice(clientIndex, 1);
        // }

    };

window.db = db;
var url = "window.location.origin/getdata/profile/";
$.get(url,function(data,status){
    // console.log(data);
    // console.log(JSON.parse(data.replaceAll("'",'"')));
    data = data.replaceAll("'",'"');
    db.data=JSON.parse(data);
    console.log(db.data[0]);
    $('#grid').jsGrid({data:db.data});
    addaction();
});
    


    // c = $('#data').text().replaceAll("'",'"');
 // console.log(JSON.parse(c));
    // db.data = JSON.parse(c);
    function addaction(){
      $('.jsgrid-filter-row').children('td').each(function(){
            $(this).children('input').attr('onkeypress','filter()');
          });
        $('.jsgrid-table tbody tr').click(function(){

            $('.jsgrid-edit-row').attr('onkeypress','editing(this)');
          });
    }
db.trainingmode = [
        { Name: "Offline", Id: 'Offline' },
        { Name: "Online", Id: 'Online' }
    ];
}());
        function editing(x){
          rowIndex = x.rowIndex;
          // alert(x.rowIndex);
          var keycode = (event.keyCode ? event.keyCode : event.which);
          if(keycode == '13'){
            // alert($('.jsgrid-edit-row').rowIndex);
              edit_row = [];
              $('.jsgrid-edit-row').children('td').each(function(){
                edit_row.push($(this).children('input').val())
              });
              db.updateItem(rowIndex,edit_row);
            }
        }
          function filter(){
            var keycode = (event.keyCode ? event.keyCode : event.which);
              if(keycode == '13'){
                // console.log(typeof($('#jsGrid1').jsGrid("getFilter").name));
                a=db.loadData($('#grid').jsGrid("getFilter"));
                $('#grid').jsGrid({data:a});

              }
              // addaction();
              $('.jsgrid-filter-row').children('td').each(function(){
                $(this).children('input').attr('onkeypress','filter()');
              })
              $('.jsgrid-table tbody tr').click(function(){
                $('.jsgrid-edit-row').attr('onkeypress','editing()');
              });
          }
          // $('td').click(function(){
          //   addaction()''
          // })