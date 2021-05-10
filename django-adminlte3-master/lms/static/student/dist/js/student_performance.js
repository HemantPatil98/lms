(function() {

    var db = {

        // loadData: function(filter) {
        //     // console.log(filter['NAME']);
        //    return $.grep(db.data, function(client) {
        //         // console.log(client['NAME']);
        //         var flag=false;
        //         $.each(Object.keys(client),function(key,val){
        //             // console.log(client[val].toString()).indexOf(filter[val].toString());
        //             val=val.toString();
        //             val1=client[val].toString();
        //             val2=filter[val];
        //             // console.log(filter.rowIndex);
        //             // console.log(val,val1,val2);
        //             if (!val2 || val2==undefined || val1.indexOf(val2) > -1){

        //             flag=true;
        //             }else{
        //                 // console.log(client);
        //                 flag=false;
        //                 return false;
        //             };
        //         })
        //         // console.log(flag);
        //         if (flag) {
        //             return client;
        //         }
        //     });
        // },
        // loadData: function(filter) {
                    // console.log(filter.name);
            // return $.grep(this.data, function(client) {
                // console.log(!filter.name || client.name.indexOf(filter.name)>-1);
                // return (!filter.ID || client.ID.indexOf(filter.ID) > -1)
                // && (!filter.NAME || client.NAME.indexOf(filter.NAME) > -1)
                // && (!filter.CONTACT || client.contact.indexOf(filter.contact) > -1)
                // && (!filter['EMAIL ID'] || client['EMAIL ID'].indexOf(filter['EMAIL ID']) > -1)
                // && (!filter['DATE OF ADMISSION'] || client['DATE OF ADMISSION'].indexOf(filter['DATE OF ADMISSION']) > -1)
                // && (!filter['TRAINING MODE'] || client['TRAINING MODE'].indexOf(filter['TRAINING MODE']) > -1)
                // && (!filter['BATCH START DATE'] || client['BATCH START DATE'].indexOf(filter['BATCH START DATE']) > -1)
                // && (!filter['COURSE'] || client['COURSE'].indexOf(filter['COURSE']) > -1)
                // && (!filter['COURSE START FROM'] || client['COURSE START FROM'].indexOf(filter['COURSE START FROM']) > -1)
                // && (!filter['CURRENT MODULE'] || client['CURRENT MODULE'].indexOf(filter['CURRENT MODULE']) > -1)
                // && (!filter['C TRAINER NAME'] || client['C TRAINER NAME'].indexOf(filter['C TRAINER NAME']) > -1)
                // && (!filter['C MODULE START DATE'] || client['C MODULE START DATE'].indexOf(filter['C MODULE START DATE']) > -1)
                // && (!filter['C MODULE END DATE'] || client['C MODULE END DATE'].indexOf(filter['C MODULE END DATE']) > -1)
                // && (!filter.ctheory || client.ctheory.indexOf(filter.ctheory) > -1)
                // && (!filter.cpracticle || client.cpracticle.indexOf(filter.cpracticle) > -1)
                // && (!filter.coral || client.coral.indexOf(filter.coral) > -1)
                // && (!filter.ctotal || client.ctotal.indexOf(filter.ctotal) > -1)
                // && (!filter.sqltrainername || client.sqltrainername.indexOf(filter.sqltrainername) > -1)
                // && (!filter.sqlmodulestartdate || client.sqlmodulestartdate.indexOf(filter.sqlmodulestartdate) > -1)
                // && (!filter.sqlmoduleenddate || client.sqlmoduleenddate.indexOf(filter.sqlmoduleenddate) > -1)
                // && (!filter.sqltheory || client.sqltheory.indexOf(filter.sqltheory) > -1)
                // && (!filter.sqlpracticle || client.sqlpracticle.indexOf(filter.sqlpracticle) > -1)
                // && (!filter.sqloral || client.sqloral.indexOf(filter.sqloral) > -1)
                // && (!filter.sqltotal || client.sqltotal.indexOf(filter.sqltotal) > -1)
                // && (!filter.wdtrainername || client.wdtrainername.indexOf(filter.wdtrainername) > -1)
                // && (!filter.wdmodulestartdate || client.wdmodulestartdate.indexOf(filter.wdmodulestartdate) > -1)
                // && (!filter.wdmoduleenddate || client.wdmoduleenddate.indexOf(filter.wdmoduleenddate) > -1)
                // // && (!filter.wdtheory || client.wdctheory.indexOf(filter.wdtheory) > -1)
                // && (!filter.wdpracticle || client.wdpracticle.indexOf(filter.wdpracticle) > -1)
                // && (!filter.wdoral || client.wdoral.indexOf(filter.wdoral) > -1)
                // && (!filter.wdtotal || client.wdtotal.indexOf(filter.wdtotal) > -1)
                // && (!filter.portfoliolink || client.portfoliolink.indexOf(filter.portfoliolink) > -1)
                // && (!filter.mock1 || client.mock1.indexOf(filter.mock1) > -1)
                // && (!filter.coretrainername || client.coretrainername.indexOf(filter.coretrainername) > -1)
                // && (!filter.coremodulestartdate || client.coremodulestartdate.indexOf(filter.coremodulestartdate) > -1)
                // && (!filter.coremoduleenddate || client.coremoduleenddate.indexOf(filter.coremoduleenddate) > -1)
                // && (!filter.coretheory || client.coretheory.indexOf(filter.coretheory) > -1)
                // && (!filter.corepracticle || client.corepracticle.indexOf(filter.corepracticle) > -1)
                // && (!filter.coreoral || client.coreoral.indexOf(filter.coreoral) > -1)
                // && (!filter.coretotal || client.coretotal.indexOf(filter.coretotal) > -1)
                // && (!filter.mock2 || client.mock2.indexOf(filter.mock2) > -1)
                // && (!filter.advtrainername || client.advtrainername.indexOf(filter.advtrainername) > -1)
                // && (!filter.advmodulestartdate || client.advmodulestartdate.indexOf(filter.advmodulestartdate) > -1)
                // && (!filter.advmoduleenddate || client.advmoduleenddate.indexOf(filter.advmoduleenddate) > -1)
                // && (!filter.advtheory || client.advtheory.indexOf(filter.advtheory) > -1)
                // && (!filter.advpracticle || client.advpracticle.indexOf(filter.advpracticle) > -1)
                // && (!filter.advoral || client.advoral.indexOf(filter.advoral) > -1)
                // && (!filter.advtotal || client.advtotal.indexOf(filter.advtotal) > -1)
                // && (!filter.fullcourseenddate || client.fullcourseenddate.indexOf(filter.fullcourseenddate) > -1)
                // && (!filter.cravitaprojectstartdate || client.cravitaprojectstartdate.indexOf(filter.cravitaprojectstartdate) > -1)
                // && (!filter.mock3 || client.mock3.indexOf(filter.mock3) > -1)
                // && (!filter.softskillmark || client.softskillmark.indexOf(filter.softskillmark) > -1)
                // && (!filter.finalmock || client.finalmock.indexOf(filter.finalmock) > -1)
                // && (!filter.totalmarks || client.totalmarks.indexOf(filter.totalmarks) > -1)
                // && (!filter.eligibleforplcement || client.eligibleforplcement.indexOf(filter.eligibleforplcement) > -1)
                // && (!filter.remark || client.remark.indexOf(filter.remark) > -1);

            // });
            // return $.grep(this.data,function(element){
            //         flag = false;

            //     $.each(Object.keys(db.data[0]),function(){
            //         // console.log(this.toString());
            //         key = this.toString();
            //         console.log(!filter[key]||element[key].indexOf(filter[key])>-1);
            //         if (!filter[key]||element[key].indexOf(filter[key])>-1){
            //         flag = true;
            //     }else{
            //         flag=false;
            //     }
            //     });
            //     if(flag){
            //         // console.log(element);
            //         return element;
            //     }
                
            // })
        // },

        // insertItem: function(insertingClient) {
        //     this.clients.push(insertingClient);
        // },

        // updateItem: function(rowIndex,updatingRow) { 
        //     console.log(updatingRow);
        //     // alert(1);
        //     pageIndex=$("#grid").jsGrid("option", "pageIndex");
        //     pageSize=$("#grid").jsGrid("option", "pageSize");
        //     console.log((pageSize*(pageIndex-1))+rowIndex);
        //     recordValue=(pageSize*(pageIndex-1))+rowIndex;
        //     Url = 'http://127.0.0.1:8000/setdata/performance/?row='+recordValue+'&rowv='+updatingRow;
        //     data={
        //         row:updatingRow,
        //     }
        //     // $('.btn').click(function(){
        //         $.get(Url,function(data,status){
        //             console.log(data);
        //         });
        //     // });
        // },

        // deleteItem: function(deletingClient) {
        //     var clientIndex = $.inArray(deletingClient, this.clients);
        //     this.clients.splice(clientIndex, 1);
        // }

    };

// window.db = db;
// var url = "http://127.0.0.1:8000/getdata/performance/";
// $.get(url,function(data,status){
//     // console.log(data);
//     // console.log(JSON.parse(data.replaceAll("'",'"')));
//     data = data.replaceAll("'",'"');
//     db.data=JSON.parse(data);
//     console.log(db.data);
//     $('#grid').jsGrid({data:db.data});

//     db.loadData;
//     // addaction();
//     $(".jsgrid-grid-body").keypress(function(){var keycode = (event.keyCode ? event.keyCode : event.which);
//           if(keycode == '13'){window.edit_row=this;$('#grid').jsGrid('updateItem')}});
//     // $(".jsgrid-filter-row").keypress(function(){var keycode = (event.keyCode ? event.keyCode : event.which);
//           // if(keycode == '13'){$('#grid').jsGrid('loadData',$('#grid').jsGrid('getFilter'))}})
//           // $('.jsgrid-filter-row').children('td').each(function(){
//           //   $(this).children('input').attr('onkeypress','filter()');
//           // });
// });
    


    // c = $('#data').text().replaceAll("'",'"');
 // console.log(JSON.parse(c));
    // db.data = JSON.parse(c);
    
db.trainingmode = [
        { Name: "Offline", Id: 'Offline' },
        { Name: "Online", Id: 'Online' }
    ];
}());
// function addaction(){
//     console.log("in action");
//       $('.jsgrid-filter-row').children('td').each(function(){
//             $(this).children('input').attr('onkeypress','filter()');
//           });
//         $('.jsgrid-table tbody tr').click(function(){

//             $('.jsgrid-edit-row').attr('onkeypress','editing(this)');
//           });
//     }
//         function editing(x){
//             var rowIndex = x.rowIndex;
//           var keycode = (event.keyCode ? event.keyCode : event.which);
//           if(keycode == '13'){
//               edit_row = [];
//               $('.jsgrid-edit-row').children('td').each(function(){
//                 edit_row.push($(this).children('input').val())
//               });
//               db.updateItem(rowIndex,edit_row);
//             }
//         }
//           function filter(){
//             var keycode = (event.keyCode ? event.keyCode : event.which);
//               if(keycode == '13'){
//                 // console.log(typeof($('#jsGrid1').jsGrid("getFilter").name));
//                 // a=db.loadData($('#grid').jsGrid("getFilter"));
//                 // $('#grid').jsGrid({data:a});
//                 // $("#grid").jsGrid("loadData");

//               }
//               // addaction();
//               $('.jsgrid-filter-row').children('td').each(function(){
//                 $(this).children('input').attr('onkeypress','filter()');
//               })
//               $('.jsgrid-table tbody tr').click(function(){
//                 $('.jsgrid-edit-row').attr('onkeypress','editing()');
//               });
//           }
//           // $('td').click(function(){
//           //   addaction()''
//           // })